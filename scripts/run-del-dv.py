# -*- coding: utf-8 -*-
from plone import api

import logging
import transaction


portal = obj  # noqa
logger = logging.getLogger('del dv')
types = ['dmsincomingmail', 'dmsincoming_email', 'dmsoutgoingmail']
count = 0

pc = portal.portal_catalog
brains = pc.unrestrictedSearchResults(portal_type=types)
for brain in brains:
    mail = brain.getObject()
    for contained in mail.objectValues():
        if contained.__class__.__name__ in ['DmsFile', 'DmsAppendixFile', 'ImioDmsFile']:
            count += 1
            api.content.delete(obj=contained, check_linkintegrity=False)

logger.warn('Deleted {} files'.format(count))
transaction.commit()
