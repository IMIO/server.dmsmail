# -*- coding: utf-8 -*-
from collections import OrderedDict
from imio.pyutils.system import error
from Products.CPUtils.Extensions.utils import check_role
from xml.etree import ElementTree as ET

import sys

portal = obj  # noqa
if not check_role(portal):
    sys.exit("You must have a manager role to run this script")
check = False
if sys.argv[-1] == 'check':
    check = True
zcmls = [
    'src/collective.behavior.internalnumber/src/collective/behavior/internalnumber/configure.zcml',
    'parts/omelette/collective/documentviewer/dexterity.zcml',
    'src/collective.classification.tree/src/collective/classification/tree/contents/configure.zcml',
    'src/collective.classification.folder/src/collective/classification/folder/content/configure.zcml',
    'src/collective.contact.core/src/collective/contact/core/configure.zcml',
    'src/collective.contact.plonegroup/src/collective/contact/plonegroup/configure.zcml',
    'src/collective.contact.plonegroup/src/collective/contact/plonegroup/subscribers.zcml',
    'src/collective.dms.basecontent/src/collective/dms/basecontent/configure.zcml',
    'src/collective.dms.mailcontent/src/collective/dms/mailcontent/configure.zcml',
    'src/collective.querynextprev/src/collective/querynextprev/subscribers.zcml',
    'src/collective.task/src/collective/task/subscribers.zcml',
    'src/imio.helpers/src/imio/helpers/events.zcml',
    'src/dexterity.localroles/src/dexterity/localroles/subscribers.zcml',
    'src/dexterity.localrolesfield/src/dexterity/localrolesfield/subscribers.zcml',
    'src/dexterity.localrolesfield/src/dexterity/localrolesfield/configure.zcml',
    'src/imio.dms.mail/imio/dms/mail/subscribers.zcml'
]


def resolve_for(dic, flag, fil):
    new_dic = {'set': flag, 'handler': resolve_path(fil, dic.pop('handler'))}
    sfor = dic.pop('for').split()  # split on multiple spaces
    new_dic['if'] = resolve_path(fil, sfor.pop(0))
    new_dic['evt'] = len(sfor) and resolve_path(fil, sfor.pop(0)) or ''
    if len(sfor):
        error('Found unexpected value in for: {}'.format(sfor))
    if len(dic):
        error('Found unhandled attributes: {}'.format(dic))
    return new_dic


def resolve_path(fil, value):
    if not value.startswith('.'):
        return value
    fparts = fil.split('/')
    if fparts[0] == 'src':
        product = fparts[1]
        start = 2
        if fparts[2] == 'src':
            start = 3
        ns_parts = len(product.split('.'))
    elif fparts[0] == 'parts':
        # asserting product name is in 2 parts
        product = '{}.{}'.format(fparts[2], fparts[3])
        start = 2
        ns_parts = 2
    rel_path = '.'.join(fparts[start+ns_parts:-1])  # can be '' or 'content'
    return '{}{}{}'.format(product, rel_path and '.{}'.format(rel_path) or '', value)


res = OrderedDict([])
for zcml in zcmls:
    res[zcml] = []
    tree = ET.parse(zcml)
    root = tree.getroot()
    for child in root:
        if child.tag.endswith('subscriber'):
            res[zcml].append(resolve_for(child.attrib, 'set', zcml))
        elif child.tag.endswith('unconfigure'):
            for subchild in child:
                if subchild.tag.endswith('subscriber'):
                    res[zcml].append(resolve_for(subchild.attrib, 'unset', zcml))
itfs = OrderedDict([])
for zcml in res:
    for tag in res[zcml]:
        by_if = itfs.setdefault(tag.pop('if'), OrderedDict([('unset', [])]))
        evt = tag.pop('evt')
        status = tag.pop('set')
        if status == 'unset':
            by_if['unset'].append((evt, tag))
        else:
            by_evt = by_if.setdefault(evt, [])
            by_evt.append(tag)

itf_fmt = '''
{}
{}'''
evt_fmt = '''
* {}'''
hdl_fmt = '''
  * .. autofunction:: {}'''

for itf in itfs:
    if not check:
        print(itf_fmt.format(itf, '-'*len(itf)))
    unset = itfs[itf].pop('unset')
    if unset:
        print('\n* UNCONFIGURE:')
        for evt, decl in unset:
            print('\n  * {}\n\n    * .. autofunction:: {}'.format(evt and evt or itf, decl['handler']))
    for evt in sorted(itfs[itf].keys()):
        if not check:
            print(evt_fmt.format(evt and evt or itf))
        for decl in itfs[itf][evt]:
            if check:
                print('{}: {}, {}'.format(itf, evt, decl['handler']))
            else:
                print(hdl_fmt.format(decl['handler']))
