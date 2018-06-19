# -*- coding: utf-8 -*-
import copy
import os
from collections import OrderedDict
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import modified
from z3c.relationfield.relation import RelationValue
import phonenumbers
from plone import api
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.app.uuid.utils import uuidToObject
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.utils import safe_unicode
from Products.CPUtils.Extensions.utils import check_zope_admin

from collective.behavior.internalnumber.behavior import IInternalNumberBehavior
from collective.contact.plonegroup.config import ORGANIZATIONS_REGISTRY

from imio.dms.mail.Extensions.imports import change_levels, sort_by_level, assert_value_in_list, assert_date
from imio.pyutils import system


def safe_encode(value, encoding='utf-8'):
    """
        Converts a value to encoding, even if it is already encoded.
    """
    if isinstance(value, unicode):
        return value.encode(encoding)
    return value


def get_organizations(self, obj=False):
    registry = getUtility(IRegistry)
    terms = []
    for uid in registry[ORGANIZATIONS_REGISTRY]:
        title = uuidToObject(uid).get_full_title(separator=' - ', first_index=1)
        terms.append((uid, title))
    if obj:
        return terms
    return '\n'.join(['%s;%s' % (t[0], t[1]) for t in terms])


def import_principals(self, add_user='', create_file='', dochange=''):
    """
        Import principals from the file 'Extensions/principals.csv' containing
        GroupId;GroupTitle;Userid;Name;email;Validateur;Éditeur;Lecteur;Encodeur
    """
    if not check_zope_admin():
        return "You must be a zope manager to run this script"
    exm = self.REQUEST['PUBLISHED']
    path = os.path.dirname(exm.filepath())
    #path = '%s/../../Extensions' % os.environ.get('INSTANCE_HOME')
    out = []
    cf = False
    if create_file == '1':
        cf = True
    doit = False
    if dochange == '1':
        doit = True

    orgas = get_organizations(self, obj=True)

    if cf:
        out.append("Creating file principals_gen.csv")
        lines = ["GroupId;GroupTitle;Userid;Name;email;Validateur;Éditeur;Lecteur;Encodeur"]
        for uid, title in orgas:
            lines.append("%s;%s;;;;;;;" %
                        (uid, title.encode('utf8')))
        if doit:
            fh = open(os.path.join(path, 'principals_gen.csv'), 'w')
            for line in lines:
                fh.write("%s\n" % line)
            fh.close()
        return '\n'.join(out)

    # Open file
    lines = system.read_file(os.path.join(path, 'principals.csv'), skip_empty=True)
    regtool = self.portal_registration
    cu = False
    if add_user == '1':
        cu = True
    cf = False
    if create_file == '1':
        cf = True
    i = 0
    for line in lines:
        i += 1
        if i == 1:
            continue
        try:
            data = line.split(';')
            orgid = data[0]
            orgtit = data[1].strip()
            userid = data[2]
            fullname = data[3]
            email = data[4]
            validateur = data[5]
            editeur = data[6]
            lecteur = data[7]
            encodeur = data[8]
        except Exception, ex:
            return "Problem line %d, '%s': %s" % (i, line, safe_encode(ex.message))
        # check userid
        if not userid.isalnum() or not userid.islower():
            out.append("Line %d: userid '%s' is not alpha lowercase" % (i, userid))
            continue
        # check user
        user = api.user.get(username=userid)
        if user is None:
            if not cu:
                out.append("Line %d: userid '%s' not found" % (i, userid))
                continue
            else:
                try:
                    out.append("=> Create user '%s': '%s', '%s'" % (userid, fullname, email))
                    if doit:
                        user = api.user.create(username=userid, email=email, password=regtool.generatePassword(),
                                               properties={'fullname': fullname},
                                               )
                except Exception, ex:
                    out.append("Line %d, cannot create user: %s" % (i, safe_encode(ex.message)))
                    continue
        # groups
        if user is not None:
            try:
                groups = api.group.get_groups(username=userid)
            except Exception, ex:
                if user is not None:
                    out.append("Line %d, cannot get groups of userid '%s': %s" % (i, userid, safe_encode(ex.message)))
                # continue
        else:
            groups = []

        # check organization
        if orgid:
            if not [uid for uid, tit in orgas if uid == orgid]:
                out.append("Line %d, cannot find org_uid '%s' in organizations" % (i, orgid))
                continue
        else:
            tmp = [uid for uid, tit in orgas if tit == safe_unicode(orgtit)]
            if tmp:
                orgid = tmp[0]
            else:
                out.append("Line %d, cannot find org_uid from org title '%s'" % (i, orgtit))
                continue

        for (name, value) in [('validateur', validateur), ('editeur', editeur), ('lecteur', lecteur),
                              ('encodeur', encodeur)]:
            value = value.strip()
            if not value:
                # We don't remove a user from a group
                continue
            # check groupid
            gid = "%s_%s" % (orgid, name)
            group = api.group.get(groupname=gid)
            if group is None:
                out.append("Line %d: groupid '%s' not found" % (i, gid))
                continue
            # add user in group
            if gid not in groups:
                out.append("=> Add user '%s' to group '%s' (%s)" % (userid, gid, orgtit))
                if doit:
                    try:
                        api.group.add_user(groupname=gid, username=userid)
                    except Exception, ex:
                        out.append("Line %d, cannot add userid '%s' to group '%s': %s"
                                   % (i, userid, gid, safe_encode(ex.message)))
    return '\n'.join(out)


def import_contacts(self, dochange='', ownorg='', only='ORGS|PERS|HP'):
    """
        Import contacts from several files in 'Extensions'
        * organizations.csv:    ID;ID Parent;Intitulé;Description;Type;Adr par;Rue;Numéro;Comp adr;CP;Localité;Tél;Gsm;
                                Fax;Courriel;Site;Région;Pays;UID
        * persons.csv:  ID;Nom;Prénom;Genre;Civilité;Naissance;Adr par;Rue;Numéro;Comp adr;CP;Localité;Tél;Gsm;
                        Fax;Courriel;Site;Région;Pays;Num int;UID
        * positions.csv:    ID;ID org;Intitulé;Description;Type;Adr par;Rue;Numéro;Comp adr;CP;Localité;Tél;Gsm;Fax;
                            Courriel;Site;Région;Pays;UID
        * heldpositions.csv:    ID;ID person;ID org;ID fct;Intitulé fct;Début fct;Fin fct;Adr par;Rue;Numéro;Comp adr;
                                CP;Localité;Tél;Gsm;Fax;Courriel;Site;Région;Pays;UID
    """
    if not check_zope_admin():
        return "You must be a zope manager to run this script"
    doit = False
    if dochange not in ('', '0', 'False', 'false'):
        doit = True
    exm = self.REQUEST['PUBLISHED']
    portal = api.portal.get()
    contacts = portal['contacts']

    def digit(phone):
        # filter with str.isdigit or unicode.isdigit
        return filter(type(phone).isdigit, phone)

    def is_zip(zipc, line, typ, country):
        ozipc = zipc
        zipc = digit(zipc)
        if ozipc != zipc:
            out.append("!! %s: line %d, zip code contains non digit chars: %s" % (typ, line, zipc))
        if zipc and len(zipc) != 4 and not country:
            out.append("!! %s: line %d, zip code length not 4: %s" % (typ, line, zipc))
        if zipc in ['0']:
            return ''
        return zipc

    def check_phone(phone, line, typ, country):
        if not phone:
            return phone
        country = country.lower()
        countries = {'belgique': 'BE', 'france': 'FR'}
        if not country:
            ctry = 'BE'
        elif country in countries:
            ctry = countries[country]
        else:
            out.append("!! %s: line %d, country not detected '%s', phone number: '%s'" % (typ, line, country, phone))
            return phone
        try:
            number = phonenumbers.parse(phone, ctry)
        except phonenumbers.NumberParseException:
            out.append("!! %s: line %d, bad phone number: %s" % (typ, line, phone))
            return ''
        if not phonenumbers.is_valid_number(number):
            out.append("!! %s: line %d, invalid phone number: %s" % (typ, line, phone))
            return ''
        return phone

    org_infos = {}
    for typ in ['types', 'levels']:
        org_infos[typ] = OrderedDict([(t['name'], t['token']) for t in getattr(contacts, 'organization_%s' % typ)])
        if not len(org_infos[typ]):
            org_infos[typ] = OrderedDict([(u'Non défini', 'non-defini')])
    org_infos_o = copy.deepcopy(org_infos)
    # read the organization file
    path = os.path.dirname(exm.filepath())
    lines = []
    if 'ORGS' in only:
        lines = system.read_csv(os.path.join(path, 'organizations.csv'), strip_chars=' ', strict=True)
    if lines:
        data = lines.pop(0)
        lendata = len(data)
        if lendata < 19 or data[18] != 'UID':
            return "!! Problem decoding first line: bad columns in organizations.csv ?"
    orgs = OrderedDict()
    uids = {}
    childs = {}
    idnormalizer = getUtility(IIDNormalizer)
    out = ["## ORGANIZATIONS ##\n"]
    for i, data in enumerate(lines, start=2):
        if len(data) != lendata:
            return "!! ORGS: problem line %d, invalid column number %d <> %d: %s" % (i, lendata, len(data),
                                                                                     ['%s' % cell for cell in data])
        id, idp, uid = data[0], data[1], data[18]
        if not id or id in orgs:
            return "!! ORGS: problem line %d, invalid id: %s" % (i, id)
        if uid in uids:
            return "!! ORGS: problem line %d, duplicated uid: %s, already found line %s" % (i, uid, uids[uid])
        elif uid:
            uids[uid] = 'orgs: %d' % i
        # ID;ID Par;Intitulé;Description;Type;Use par adr,Rue;Numéro;Comp adr;CP;Localité;Tél;Gsm;Fax;Courriel;Site;
        # Région;Pays;UID
        orgs[id] = {'lev': 1, 'prt': idp, 'tit': data[2], 'desc': data[3], 'upa': data[5] and int(data[5]) or '',
                    'st': data[6], 'nb': data[7], 'box': data[8], 'zip': is_zip(data[9], i, 'ORGS', data[17]),
                    'loc': data[10], 'tel': check_phone(digit(data[11]), i, 'ORGS', data[17]),
                    'mob': check_phone(digit(data[12]), i, 'ORGS', data[17]),
                    'fax': check_phone(digit(data[13]), i, 'ORGS', data[17]), 'eml': data[14],
                    'www': data[15], 'dep': data[16], 'cty': data[17], 'uid': uid}
        typ = 'types'
        if idp:
            typ = 'levels'
            if idp not in childs:
                childs[idp] = []
            childs[idp].append(id)
        if data[4]:
            utyp = safe_unicode(data[4])
            if utyp not in org_infos[typ]:
                org_infos[typ][utyp] = idnormalizer.normalize(utyp)
            orgs[id]['typ'] = org_infos[typ][utyp]
        else:  # we take the first value
            orgs[id]['typ'] = org_infos[typ].values()[0]

    # adapt organization levels and sort
    for idp in childs:
        change_levels(idp, childs, orgs)
    orgs = sort_by_level(orgs)

    # updating contacts options
    for typ in ['types', 'levels']:
        if len(org_infos[typ]) != len(org_infos_o[typ]):
            out.append("Contacts parameter modification 'organization_%s'" % typ)
            if doit:
                setattr(contacts, 'organization_%s' % typ,
                        [{'name': i[0], 'token': i[1]} for i in org_infos[typ].items()])
                out.append("New value: %s" % [{'name': safe_encode(i[0]),
                                               'token': i[1]} for i in org_infos[typ].items()])
            else:
                out.append("New value will be: %s" % [{'name': safe_encode(i[0]),
                                                       'token': i[1]} for i in org_infos[typ].items()])

    # creating organization
    for i, id in enumerate(orgs, start=2):
        det = orgs[id]
        if det['lev'] == 1:
            cont = contacts
        else:
            # get the container organization, already created
            cont = orgs[det['prt']].get('obj', orgs[det['prt']]['tit'])
        action = 'create'
        if det['uid']:
            obj = uuidToObject(det['uid'])
            if not obj:
                out.append("!! %04d org: cannot find obj from uuid %s: SKIPPED" % det['uid'])
                continue
            else:
                action = 'update'
        elif ownorg and ownorg == det['tit']:
            obj = contacts['plonegroup-organization']
            action = 'update'
            det['upa'] = False
        if action == 'create':
            if doit:
                obj = api.content.create(container=cont, type='organization', title=safe_unicode(det['tit']),
                                         description=safe_unicode(det['desc']), organization_type=det['typ'],
                                         street=safe_unicode(det['st']), number=safe_unicode(det['nb']),
                                         additional_address_details=safe_unicode(det['box']),
                                         zip_code=safe_unicode(det['zip']), city=safe_unicode(det['loc']),
                                         phone=safe_unicode(det['tel']), cell_phone=safe_unicode(det['mob']),
                                         fax=safe_unicode(det['fax']), email=safe_unicode(det['eml']),
                                         website=safe_unicode(det['www']), region=safe_unicode(det['dep']),
                                         country=safe_unicode(det['cty']), use_parent_address=bool(det['upa']))
                det['obj'] = obj
                out.append("%04d org: new orga '%s' created in %s" % (i, safe_encode(det['tit']), safe_encode(cont)))
            else:
                out.append("%04d org: new orga '%s' will be created in %s" % (i, safe_encode(det['tit']),
                                                                              safe_encode(cont)))
        elif action == 'update':
            attrs = {'title': 'tit', 'description': 'desc', 'street': 'st', 'number': 'nb',
                     'additional_address_details': 'box', 'zip_code': 'zip', 'city': 'loc', 'phone': 'tel',
                     'cell_phone': 'mob', 'fax': 'fax', 'email': 'eml', 'website': 'www', 'region': 'dep',
                     'country': 'cty', 'organization_type': det['typ'], 'use_parent_address': bool(det['upa'])}
            change = False
            changed = []
            for attr, new_val in attrs.items():
                if attr not in ('organization_type', 'use_parent_address'):
                    new_val = safe_unicode(det[new_val])
                act_val = getattr(obj, attr)
                if act_val != new_val and not (act_val is None and new_val == u''):
                    if doit:
                        if new_val == '':
                            new_val = None
                        setattr(obj, attr, new_val)
                    change = True
                    changed.append(attr)
            if change and doit:
                obj.reindexObject()
                modified(obj)
            det['obj'] = obj
            status = ''
            if not doit:
                status = 'will be '
            if change:
                status += 'REALLY '
            else:
                status += 'not '
            out.append("%04d org: '%s' %supdated, %s" % (i, obj.absolute_url(), status, changed))

    # read the persons file
    lines = []
    if 'PERS' in only:
        lines = system.read_csv(os.path.join(path, 'persons.csv'), strip_chars=' ', strict=True)
    # ID;Nom;Prénom;Genre;Civilité;Naissance;Adr par;Rue;Numéro;Comp adr;CP;Localité;Tél;Gsm;
    # Fax;Courriel;Site;Région;Pays;Num int;UID
    if lines:
        data = lines.pop(0)
        lendata = len(data)
        if lendata < 21 or data[20] != 'UID':
            return "Problem decoding first line: bad columns in persons.csv ?"
    persons = {}
    out.append("\n## PERSONS ##\n")

    for i, data in enumerate(lines, start=2):
        if len(data) != lendata:
            return "!! PERS: problem line %d, invalid column number %d <> %d: %s" % (i, lendata, len(data),
                                                                                     ['%s' % cell for cell in data])
        id, name, fname, inum, uid = data[0], data[1], data[2], data[19], data[20]
        errors = []
        try:
            upa = data[6] and int(data[6]) or ''
            phone = safe_unicode(check_phone(digit(data[12]), i, 'PERS', data[18]))
            cell_phone = safe_unicode(check_phone(digit(data[13]), i, 'PERS', data[18]))
            fax = safe_unicode(check_phone(digit(data[14]), i, 'PERS', data[18]))
            zipc = safe_unicode(is_zip(data[10], i, 'PERS', data[18]))
            gender = assert_value_in_list(data[3], ['', 'F', 'M'])
            birthday = assert_date(data[5])
        except AssertionError, ex:
            errors.append("!! PERS: problem line %d: %s" % (i, safe_encode(ex.message)))
        except Exception, ex:
            errors.append("!! PERS: problem line %d, '%s': %s" % (i, '|'.join(data), safe_encode(ex.message)))
        if not id or id in persons:
            errors.append("!! PERS: problem line %d, invalid id: %s" % (i, id))
        if uid in uids:
            errors.append("!! PERS: problem line %d, duplicated uid: %s, already found line %s" % (i, uid, uids[uid]))
        elif uid:
            uids[uid] = 'pers: %d' % i
        if errors:
            if doit:
                return '\n'.join(errors)
            out.append('\n'.join(errors))

        persons[id] = {}
        action = 'create'
        if uid:
            obj = uuidToObject(uid)
            if not obj:
                out.append("!! PERS %04d: cannot find obj from uuid %s: SKIPPED" % uid)
                continue
            else:
                action = 'update'
        elif inum:
            brains = api.content.find(portal_type='person', internal_number=inum)
            if len(brains) == 1:
                obj = brains[0].getObject()
                action = 'update'
            elif len(brains) > 1:
                out.append("!! PERS %04d: multiple persons found with int number '%s': SKIPPED (%s)" % (i, inum,
                           ','.join([b.getPath() for b in brains])))
                continue
        if action == 'create':
            if doit:
                real_id = new_id = idnormalizer.normalize(safe_encode('%s-%s' % (fname, name)))
                count = 0
                while real_id in contacts:
                    count += 1
                    real_id = '%s-%d' % (new_id, count)

                obj = api.content.create(container=contacts, type='person', id=real_id, lastname=safe_unicode(name),
                                         firstname=safe_unicode(fname), gender=gender,
                                         person_title=safe_unicode(data[4]), birthday=birthday,
                                         street=safe_unicode(data[7]), number=safe_unicode(data[8]),
                                         additional_address_details=safe_unicode(data[9]),
                                         zip_code=zipc, city=safe_unicode(data[11]),
                                         phone=phone, cell_phone=cell_phone, fax=fax, email=safe_unicode(data[15]),
                                         website=safe_unicode(data[16]), region=safe_unicode(data[17]),
                                         country=safe_unicode(data[18]), use_parent_address=bool(upa))
                if inum and IInternalNumberBehavior.providedBy(obj):
                    obj.internal_number = inum
                    obj.reindexObject(idxs=['internal_number', 'SearchableText'])
                out.append("%04d pers: new person '%s %s' created" % (i, safe_encode(name), safe_encode(fname)))
                persons[id]['obj'] = obj
            else:
                out.append("%04d pers: new person '%s %s' will be created" % (i, safe_encode(name), safe_encode(fname)))
        elif action == 'update':
            attrs = {'lastname': 1, 'firstname': 2, 'gender': gender, 'person_title': 4, 'birthday': birthday,
                     'street': 7, 'number': 8, 'additional_address_details': 9, 'zip_code': zipc, 'city': 11,
                     'phone': phone, 'cell_phone': cell_phone, 'fax': fax, 'email': 15, 'website': 16, 'region': 17,
                     'country': 18, 'use_parent_address': bool(upa)}
            change = False
            changed = []
            for attr, new_val in attrs.items():
                if attr not in ('gender', 'birthday', 'use_parent_address', 'phone', 'cell_phone', 'fax', 'zip_code'):
                    new_val = safe_unicode(data[new_val])
                act_val = getattr(obj, attr)
                if act_val != new_val and not (act_val is None and new_val == u''):
                    if doit:
                        if new_val == '':
                            new_val = None
                        setattr(obj, attr, new_val)
                    change = True
                    changed.append(attr)
            if change and doit:
                obj.reindexObject()
                modified(obj)
            persons[id]['obj'] = obj
            status = ''
            if not doit:
                status = 'will be '
            if change:
                status += 'REALLY '
            else:
                status += 'not '
            out.append("%04d pers: '%s' %supdated, %s" % (i, obj.absolute_url(), status, changed))

    # read the heldpositions file
    lines = []
    if 'HP' in only:
        lines = system.read_csv(os.path.join(path, 'heldpositions.csv'), strip_chars=' ', strict=True)
    # ID;ID person;ID org;ID fct;Intitulé fct;Début fct;Fin fct;Adr par;Rue;Numéro;Comp adr;
    # CP;Localité;Tél;Gsm;Fax;Courriel;Site;Région;Pays;UID
    if lines:
        data = lines.pop(0)
        lendata = len(data)
        if lendata < 21 or data[20] != 'UID':
            return "Problem decoding first line: bad columns in heldpositions.csv ?"
        intids = getUtility(IIntIds)
    hps = {}
    out.append("\n## HELD POSITIONS ##\n")
    for i, data in enumerate(lines, start=2):
        if len(data) != lendata:
            return "!! HP: problem line %d, invalid column number %d <> %d: %s" % (i, lendata, len(data),
                                                                                   ['%s' % cell for cell in data])
        id, pid, oid, title, uid = data[0], data[1], data[2], data[4], data[20]
        errors = []
        try:
            start = assert_date(data[5])
            end = assert_date(data[6])
            phone = safe_unicode(check_phone(digit(data[13]), i, 'PERS', data[19]))
            cell_phone = safe_unicode(check_phone(digit(data[14]), i, 'PERS', data[19]))
            fax = safe_unicode(check_phone(digit(data[15]), i, 'PERS', data[19]))
            upa = data[7] and int(data[7]) or ''
            zipc = safe_unicode(is_zip(data[11], i, 'HP', data[19]))
        except AssertionError, ex:
            errors.append("!! HP: problem line %d: %s" % (i, safe_encode(ex.message)))
        except Exception, ex:
            errors.append("!! HP: problem line %d, '%s': %s" % (i, '|'.join(data), safe_encode(ex.message)))
        if not id or id in hps:
            errors.append("!! HP: problem line %d, invalid id: %s" % (i, id))
        if not pid:
            errors.append("!! HP: problem line %d, invalid person id: %s" % (i, pid))
        if not oid:
            errors.append("!! HP: problem line %d, invalid org id: %s" % (i, oid))
        if uid in uids:
            errors.append("!! HP: problem line %d, duplicated uid: %s, already found line %s" % (i, uid, uids[uid]))
        elif uid:
            uids[uid] = 'hp: %d' % i
        if errors:
            if doit:
                return '\n'.join(errors)
            out.append('\n'.join(errors))

        hps[id] = {}
        action = 'create'
        if uid:
            obj = uuidToObject(uid)
            if not obj:
                out.append("!! HP %04d: cannot find obj from uuid %s: SKIPPED" % uid)
                continue
            else:
                action = 'update'
        if pid in persons:
            if 'obj' in persons[pid]:
                pers = persons[pid]['obj']
            elif not doit:
                pers = portal  # without doit in creation mode, obj not there => take portal
            else:
                pers = None
        else:
            out.append("!! HP %04d: person not found for id '%s': SKIPPED" % (i, pid))
            continue
        if oid in orgs:
            if 'obj' in orgs[oid]:
                org = orgs[oid]['obj']
            elif not doit:
                org = portal  # without doit in creation mode, obj not there => take portal
            else:
                org = None
        else:
            out.append("!! HP %04d: org not found for id '%s': SKIPPED" % (i, oid))
            continue
        if action == 'create':
            if doit:
                real_id = new_id = idnormalizer.normalize(safe_encode('%s-%s' % (safe_unicode(title), org.title)))
                count = 0
                while real_id in pers:
                    count += 1
                    real_id = '%s-%d' % (new_id, count)

                obj = api.content.create(container=pers, type='held_position', id=real_id,
                                         position=RelationValue(intids.getId(org)),
                                         label=safe_unicode(title), start_date=start, end_date=end,
                                         street=safe_unicode(data[8]), number=safe_unicode(data[9]),
                                         additional_address_details=safe_unicode(data[10]),
                                         zip_code=zipc, city=safe_unicode(data[12]),
                                         phone=phone, cell_phone=cell_phone, fax=fax, email=safe_unicode(data[16]),
                                         website=safe_unicode(data[17]), region=safe_unicode(data[18]),
                                         country=safe_unicode(data[19]), use_parent_address=bool(upa))
                out.append("%04d hp: new hp '%s' for '%s' created" % (i, safe_encode(title), pers.Title()))
                hps[id]['obj'] = obj
            else:
                out.append("%04d hp: new hp '%s %s' will be created" % (i, safe_encode(title), pers.Title()))
        elif action == 'update':
            intid = intids.getId(org)
            new_pos = obj.position
            if new_pos and new_pos.to_id != intid:
                new_pos = RelationValue(intid)
            attrs = {'position': new_pos, 'label': 4, 'start_date': start, 'end_date': end,
                     'street': 8, 'number': 9, 'additional_address_details': 10, 'zip_code': zipc, 'city': 12,
                     'phone': phone, 'cell_phone': cell_phone, 'fax': fax, 'email': 16, 'website': 17, 'region': 18,
                     'country': 19, 'use_parent_address': bool(upa)}
            change = False
            changed = []
            for attr, new_val in attrs.items():
                if attr not in ('position', 'start_date', 'end_date', 'phone', 'cell_phone', 'fax',
                                'use_parent_address', 'zip_code'):
                    new_val = safe_unicode(data[new_val])
                act_val = getattr(obj, attr)
                if act_val != new_val and not (act_val is None and new_val == u''):
                    if doit:
                        if new_val == '':
                            new_val = None
                        setattr(obj, attr, new_val)
                    change = True
                    changed.append(attr)
            if change and doit:
                obj.reindexObject()
                modified(obj)
            hps[id]['obj'] = obj
            status = ''
            if not doit:
                status = 'will be '
            if change:
                status += 'REALLY '
            else:
                status += 'not '
            out.append("%04d hp: '%s' %supdated, %s" % (i, obj.absolute_url(), status, changed))

    return '\n'.join(out)
