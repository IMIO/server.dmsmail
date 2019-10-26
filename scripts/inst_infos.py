# -*- coding: utf-8 -*-

from imio.pyutils.system import dump_var
from imio.pyutils.system import load_var
from plone import api
from Products.CPUtils.Extensions.utils import tobytes

import os

types_to_count = ('dmsincomingmail', 'dmsoutgoingmail', 'task', 'organization', 'person', 'held_position',
                  'dmsommainfile')

zopedir = os.path.expanduser("~")
dumpfile = os.path.join(zopedir, 'inst_infos.dic')
maindic = {}

# get instance name
inst = os.getenv('PWD').split('/')[-1]
dic = {inst: {'types': {}, 'users': 0, 'groups': 0, 'fs_nm': '', 'fs_sz': 0}}
infos = dic[inst]

# get dumped dictionary
load_var(dumpfile, maindic)

# obj is the portal site
portal = obj

# get types count
lengths = dict(portal.portal_catalog.Indexes['portal_type'].uniqueValues(withLengths=True))
for typ in types_to_count:
    infos['types'][typ] = lengths.get(typ, 0)

# get users count
infos['users'] = len(api.user.get_users())

# get groups count
infos['groups'] = len(api.group.get_groups())

# sizes. app is zope
dbs = app['Control_Panel']['Database']
for db in dbs.getDatabaseNames():
    size = dbs[db].db_size()
    size = int(tobytes(size[:-1] + ' ' + size[-1:] + 'B'))
    if size > infos['fs_sz']:
        infos['fs_sz'] = size
        infos['fs_nm'] = dbs[db].db_name()


# dump dictionary
maindic['inst'].update(dic)
dump_var(dumpfile, maindic)
