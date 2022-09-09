# -*- coding: utf-8 -*-
from imio.helpers.content import object_values
from plone import api


import logging
import transaction


portal = obj  # noqa
logger = logging.getLogger('del files')

types = ['dmsincomingmail', 'dmsincoming_email', 'dmsoutgoingmail']

pc = portal.portal_catalog
brains = pc.unrestrictedSearchResults(portal_type=types)
count = 0
for brain in brains:
    mail = brain.getObject()
    files = object_values(mail, ['DmsFile', 'DmsAppendixFile', 'ImioDmsFile'])
    if not files:
        continue
    count += len(files)
    api.content.delete(objects=files, check_linkintegrity=False)

logger.warn('Deleted {} files'.format(count))

transaction.commit()
