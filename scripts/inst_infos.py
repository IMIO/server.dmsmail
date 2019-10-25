# -*- coding: utf-8 -*-

from imio.pyutils.system import dump_var
from imio.pyutils.system import load_var

import os

types_to_count = ('dmsincomingmail', 'dmsoutgoingmail', 'task', 'organization', 'person', 'held_position',
                  'dmsommainfile')

zopedir = os.path.expanduser("~")
dumpfile = os.path.join(zopedir, 'inst_infos.dic')
maindic = {}

# get instance name
inst = os.getenv('PWD').split('/')[-1]
dic = {'inst': {inst: {'types': {}}}}
infos = dic['inst'][inst]

# get dumped dictionary
load_var(dumpfile, maindic)

# obj is the portal site
portal = obj

# get types count
lengths = dict(portal.portal_catalog.Indexes['portal_type'].uniqueValues(withLengths=True))
for typ in types_to_count:
    infos['types'][typ] = lengths.get(typ, 0)

# get users count

# dump dictionary
maindic.update(dic)
dump_var(dumpfile, maindic)
