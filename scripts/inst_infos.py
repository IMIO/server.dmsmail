# -*- coding: utf-8 -*-

from imio.pyutils.system import dump_var
from imio.pyutils.system import load_var
from os import path


zopedir = path.expanduser("~")
dumpfile = path.join(zopedir, 'inst_infos.dic')
maindic = {}

load_var(dumpfile, maindic)

maindic.update({1: 2})

dump_var(dumpfile, maindic)
