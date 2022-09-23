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
    for contained in mail.objectValues():
        if contained.__class__.__name__ in ['DmsFile', 'DmsAppendixFile', 'ImioDmsFile']:
            count += 1
            try:
                api.content.delete(obj=contained, check_linkintegrity=False)
            except AssertionError as error:  # in zc.relation
                logger.error("Cannot delete {}".format(contained.absolute_url()))

logger.warn('Deleted {} files'.format(count))

if doit:
    transaction.commit()
    logger.warn('Commit done')
