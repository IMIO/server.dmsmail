# -*- coding: utf-8 -*-
import os
from zope.component import getUtility
from plone import api
from plone.app.uuid.utils import uuidToObject
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.utils import safe_unicode
from Products.CPUtils.Extensions.utils import check_zope_admin
from collective.contact.plonegroup.config import ORGANIZATIONS_REGISTRY
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
