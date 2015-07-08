# -*- coding: utf-8 -*-
import os
from plone import api
from imio.pyutils import system


def import_principals(self, create='', dochange=''):
    exm = self.REQUEST['PUBLISHED']
    path = os.path.dirname(exm.filepath())
    #path = '%s/../../Extensions' % os.environ.get('INSTANCE_HOME')
    # Open file
    lines = system.read_file(os.path.join(path, 'principals.csv'), skip_empty=True)
    cu = False
    if create not in ('', '0', 'False', 'false'):
        cu = True
    doit = False
    if dochange not in ('', '0', 'False', 'false'):
        doit = True
    i = 0
    out = []
    for line in lines:
        i += 1
        if i == 1:
            continue
        try:
            data = line.split(';')
            orgid = data[0]
            orgtit = data[1]
            userid = data[2]
            fullname = data[3]
            email = data[4]
            validateur = data[5]
            encodeur = data[6]
        except Exception, ex:
            return "Problem line %d, '%s': %s" % (i, line, ex)
        # check userid
        if not userid.isalpha() or not userid.islower():
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
                        user = api.user.create(username=userid,
                                               #email='bob@plone.org',
                                               #properties={'fullname': fullname},
                                               )
                except Exception, ex:
                    out.append("Line %d, cannot create user: %s" % (i, ex))
        # groups
        groups = api.group.get_groups(username=userid)
        for (name, value) in [('validateur', validateur), ('encodeur', encodeur)]:
            value = value.strip()
            if not value:
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
                api.group.add_user(groupname=gid, username=userid)
    return '\n'.join(out)
