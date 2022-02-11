# -*- coding: utf-8 -*-

from plone import api

portal = obj  # noqa

mtypes = api.portal.get_registry_record('imio.dms.mail.browser.settings.IImioDmsMailConfig.omail_types', default=[])
mtypes = {dic.get('mt_value', dic.get('value')): {'t': dic.get('mt_title', dic.get('dtitle')), 's': None}
          for dic in mtypes}

pc = portal.portal_catalog
brains = pc.unrestrictedSearchResults(portal_type='dmsoutgoingmail')
for brain in brains:
    mt = brain.mail_type
    if mt not in mtypes:
        mtypes[brain.mail_type] = {'t': u'', 's': u'3_manquant'}
    elif mtypes[mt]['s'] is None:
        mtypes[mt]['s'] = u'2_utilisé'
out = []
for mtype in sorted(mtypes):
    if mtypes[mtype]['s'] is None:
        mtypes[mtype]['s'] = u'1_inutile'
    out.append(u"{}: '{}' => '{}'".format(mtypes[mtype]['s'], mtype, mtypes[mtype]['t']))

for line in sorted(out):
    print(line.encode('utf8'))
