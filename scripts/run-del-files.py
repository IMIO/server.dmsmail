# -*- coding: utf-8 -*-
# from imio.helpers.content import object_values
from plone import api


import logging
import sys
import transaction


portal = obj  # noqa
logger = logging.getLogger('del files')
types = ['dmsincomingmail', 'dmsincoming_email', 'dmsoutgoingmail']
doit = False
if sys.argv[-1] == 'doit':
    doit = True

pc = portal.portal_catalog
brains = pc.unrestrictedSearchResults(portal_type=types)
count = 0
for brain in brains:
    mail = brain.getObject()
    # files = object_values(mail, ['DmsFile', 'DmsAppendixFile', 'ImioDmsFile']) dmsmail 3.0 only
    for contained in mail.objectValues():  # works with dmsmail 2.3
        if contained.__class__.__name__ in ['DmsFile', 'DmsAppendixFile', 'ImioDmsFile']:
            count += 1
            api.content.delete(obj=contained, check_linkintegrity=False)

logger.warn('Deleted {} files'.format(count))

if doit:
    transaction.commit()
    logger.warn('Commit done')
