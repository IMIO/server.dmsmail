# -*- coding: utf-8 -*-
from plone import api
import logging
import transaction

portal = obj  # noqa
logger = logging.getLogger('reindex')
logger.setLevel(logging.INFO)

pc = api.portal.get_tool('portal_catalog')
brains = pc.unrestrictedSearchResults(portal_type=['dmsincomingmail', 'dmsincoming_email'], sort_on='created')
import ipdb; ipdb.set_trace()
for i, brain in enumerate(brains, start=1):
    obj = brain.getObject()
    obj.reindexObjectSecurity()
    if i % 1000 == 0:
        transaction.commit()
        logger.info('Committed at {}'.format(i))

transaction.commit()
