# -*- coding: utf-8 -*-

import os
pyu_path = os.path.realpath('parts/omelette/imio/pyutils')
import sys
sys.path[0:0] = ['/'.join(pyu_path.split('/')[:-2])]

from imio.pyutils.system import error
from imio.pyutils.system import read_file
from imio.pyutils.system import verbose

import argparse


def patch_instance(inst='instance-debug'):
    idp = 'parts/{}/bin/interpreter'.format(inst)
    if not os.path.exists(idp):
        error("'{}' doesn't exist: cannot patch it".format(idp))
        return False
    lines = read_file(idp)
    if 'ploneCustom.css' not in ''.join(lines):
        sp = 0
        for (i, line) in enumerate(lines):
            if 'exec(_val)' in line:
                nl = line.lstrip()
                sp = len(line) - len(nl)
                break
        lines.insert(i, "{}{}".format(' ' * sp,
                                      '_val = _val.replace("\'); from AccessControl.SpecialUsers import system '
                                      'as user;", "/ploneCustom.css\'); from AccessControl.SpecialUsers import '
                                      'system as user;")'))
        verbose("=> Patching: '{}'".format(idp))
        fh = open(idp, 'w')
        fh.write('\n'.join(lines))
        fh.close()
    else:
        verbose("=> Already patched: '{}'".format(idp))


functions = {'patch_instance': patch_instance}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Call some helper function')
    parser.add_argument('-f', '--function', dest='fct', help="Function to call",
                        choices=sorted(functions.keys()))
    parser.add_argument('-i', '--instance', dest='inst', help="Instance to use")
    ns = parser.parse_args()
    if ns.fct:
        kwargs = {}
        if ns.inst:
            kwargs['inst'] = ns.inst
        functions[ns.fct](**kwargs)
