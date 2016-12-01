# -*- coding: utf-8 -*-
import copy
import os
from collections import OrderedDict
from zope.component import getUtility
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


def import_principals(self, create='', dochange=''):
    """
        Import principals from the file 'Extensions/principals.csv' containing
        GroupId;GroupTitle;Userid;Name;email;Validateur;Éditeur;Lecteur
    """
    if not check_zope_admin():
        return "You must be a zope manager to run this script"
    exm = self.REQUEST['PUBLISHED']
    path = os.path.dirname(exm.filepath())
    #path = '%s/../../Extensions' % os.environ.get('INSTANCE_HOME')
    # Open file
    lines = system.read_file(os.path.join(path, 'principals.csv'), skip_empty=True)
    regtool = self.portal_registration
    cu = False
    if create not in ('', '0', 'False', 'false'):
        cu = True
    doit = False
    if dochange not in ('', '0', 'False', 'false'):
        doit = True
    orgas = get_organizations(self, obj=True)
    i = 0
    out = []
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

        for (name, value) in [('validateur', validateur), ('editeur', editeur), ('lecteur', lecteur)]:
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


def import_contacts(self, dochange=''):
    """
        Import contacts from several files in 'Extensions'
        * organizations.csv:    ID;ID Parent;Intitulé;Description;Type;Rue;Numéro;Comp adr;CP;Localité;Tél;Gsm;Fax;
                                Courriel;Site;Région;Pays
        * persons.csv:  ID;Nom;Prénom;Genre;Civilité;Naissance;Rue;Numéro;Comp adr;CP;Localité;Tél;Gsm;
                        Fax;Courriel;Site;Région;Pays;Num int
        * positions.csv:    ID;ID org;Intitulé;Description;Type;Rue;Numéro;Comp adr;CP;Localité;Tél;Gsm;Fax;
                            Courriel;Site;Région;Pays
        * heldpositions.csv:    ID;ID person;ID org;ID fct;Intitulé fct;Début fct;Fin fct;
    """
    if not check_zope_admin():
        return "You must be a zope manager to run this script"
    doit = False
    if dochange not in ('', '0', 'False', 'false'):
        doit = True
    exm = self.REQUEST['PUBLISHED']
    portal = api.portal.get()
    contacts = portal['contacts']
    org_infos = {}
    for typ in ['types', 'levels']:
        org_infos[typ] = OrderedDict([(t['name'], t['token']) for t in getattr(contacts, 'organization_%s' % typ)])
        if not len(org_infos[typ]):
            org_infos[typ] = OrderedDict([(u'Non défini', 'non-defini')])
    org_infos_o = copy.deepcopy(org_infos)
    # read the organization file
    path = os.path.dirname(exm.filepath())
    lines = system.read_file(os.path.join(path, 'organizations.csv'), strip_chars=' "', skip_empty=True, skip_lines=1)
    orgs = OrderedDict()
    childs = {}
    idnormalizer = getUtility(IIDNormalizer)
    out = ["!! ORGANIZATIONS !!\n"]
    for i, line in enumerate(lines):
        try:
            data = [item.strip(' "').replace('""', '"') for item in line.split(';')]
            id = data[0]
            idp = data[1]
            last = data[16]  # just to check the number of columns
        except Exception, ex:
            return "Problem line %d, '%s': %s" % (i, line, safe_encode(ex.message))
        if not id or id in orgs:
            return "Problem line %d, invalid id: %s" % (i, id)
        # ID;ID Parent;Intitulé;Description;Type;Rue;Numéro;Comp adr;CP;Localité;Tél;Gsm;Fax;Courriel;Site;Région;Pays
        orgs[id] = {'lev': 1, 'prt': idp, 'tit': data[2], 'desc': data[3], 'st': data[5], 'nb': data[6],
                    'box': data[7], 'zip': data[8], 'loc': data[9], 'tel': data[10], 'mob': data[11], 'fax': data[12],
                    'eml': data[13], 'www': data[14], 'dep': data[15], 'cty': last}
        typ = 'types'
        if idp:
            typ = 'levels'
            if idp not in childs:
                childs[idp] = []
            childs[idp].append(id)
        if data[4]:
            if data[4] not in org_infos[typ]:
                org_infos[typ][safe_unicode(data[4])] = idnormalizer.normalize(safe_encode(data[4]))
            orgs[id]['typ'] = org_infos[typ][safe_unicode(data[4])]
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
    for i, id in enumerate(orgs, start=1):
        det = orgs[id]
        if det['lev'] == 1:
            cont = contacts
        else:
            # get the container organization, already created
            cont = orgs[det['prt']].get('obj', orgs[det['prt']]['tit'])
        if doit:
            obj = api.content.create(container=cont, type='organization', title=safe_unicode(det['tit']),
                                     description=safe_unicode(det['desc']), organization_type=det['typ'],
                                     street=safe_unicode(det['st']), number=safe_unicode(det['nb']),
                                     additional_address_details=safe_unicode(det['box']),
                                     zip_code=safe_unicode(det['zip']), city=safe_unicode(det['loc']),
                                     phone=safe_unicode(det['tel']), cell_phone=safe_unicode(det['mob']),
                                     fax=safe_unicode(det['fax']), email=safe_unicode(det['eml']),
                                     website=safe_unicode(det['www']), region=safe_unicode(det['dep']),
                                     country=safe_unicode(det['cty']), use_parent_address=False)
            det['obj'] = obj
            out.append("%04d org: new orga '%s' created in %s" % (i, safe_encode(det['tit']), safe_encode(cont)))
        else:
            out.append("%04d org: new orga '%s' will be created in %s" % (i, safe_encode(det['tit']),
                                                                          safe_encode(cont)))

    # read the persons file
    lines = system.read_file(os.path.join(path, 'persons.csv'), strip_chars=' "', skip_empty=True, skip_lines=1)
    # ID;ID org;ID fct;Nom;Prénom;Genre;Civilité;Naissance;Rue;Numéro;Comp adr;CP;Localité;Tél;Gsm;
    # Fax;Courriel;Site;Région;Pays;Intitulé fct;Début fct;Fin fct;Num int
    persons = {}
    out.append("\n!! PERSONS !!\n")
    for i, line in enumerate(lines, start=1):
        try:
            data = [item.strip(' "').replace('""', '"') for item in line.split(';')]
            id = data[0]
            name = data[1]
            fname = data[2]
            gender = assert_value_in_list(data[3], ['', 'F', 'M'])
            birthday = assert_date(data[5])
            inum = data[18]
#            last = data[23]  # just to check the number of columns
        except AssertionError, ex:
            return "Problem line %d: %s" % (i, safe_encode(ex.message))
        except Exception, ex:
            return "Problem line %d, '%s': %s" % (i, line, safe_encode(ex.message))
        if not id or id in persons:
            return "Problem line %d, invalid id: %s" % (i, id)
        persons[id] = {}
        if inum and api.content.find(portal_type='person', internal_number=inum):
            out.append("%04d pers: person '%s %s' already exists with internal number '%s'" % (i, safe_encode(name),
                       safe_encode(fname), inum))
            continue
        if doit:
            real_id = new_id = idnormalizer.normalize(safe_encode('%s-%s' % (fname, name)))
            count = 0
            while real_id in contacts:
                count += 1
                real_id = '%s-%d' % (new_id, count)

            obj = api.content.create(container=contacts, type='person', id=real_id, lastname=safe_unicode(name),
                                     firstname=safe_unicode(fname), gender=gender,
                                     person_title=safe_unicode(data[4]), birthday=birthday,
                                     street=safe_unicode(data[6]), number=safe_unicode(data[7]),
                                     additional_address_details=safe_unicode(data[8]),
                                     zip_code=safe_unicode(data[9]), city=safe_unicode(data[10]),
                                     phone=safe_unicode(data[11]), cell_phone=safe_unicode(data[12]),
                                     fax=safe_unicode(data[13]), email=safe_unicode(data[14]),
                                     website=safe_unicode(data[15]), region=safe_unicode(data[16]),
                                     country=safe_unicode(data[17]), use_parent_address=False)
            if inum and IInternalNumberBehavior.providedBy(obj):
                obj.internal_number = inum
                obj.reindexObject(idxs=['internal_number', 'SearchableText'])
            out.append("%04d pers: new person '%s %s' created" % (i, safe_encode(name), safe_encode(fname)))
        else:
            out.append("%04d pers: new person '%s %s' will be created" % (i, safe_encode(name), safe_encode(fname)))
    return '\n'.join(out)
