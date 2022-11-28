# -*- coding: utf-8 -*-
# from imio.helpers.content import object_values
from plone import api


import logging
import os
import sys
import transaction


portal = obj  # noqa
logger = logging.getLogger('del files')
types = ['dmsmainfile', 'dmsappendixfile', 'dmsommainfile']
doit = False
if sys.argv[-1] == 'doit':
    doit = True
batch_value = int(os.getenv('BATCH', '0'))

pc = portal.portal_catalog
brains = pc.unrestrictedSearchResults(portal_type=types)

for i, brain in enumerate(brains, start=1):
    # if i > 1001:
    #     sys.exit(1)
    if batch_value and i > batch_value:  # so it is possible to run this step partially
        break
    fil = brain.getObject()
    try:
        api.content.delete(obj=fil, check_linkintegrity=False)
    except AssertionError as error:  # in zc.relation
        logger.error("Cannot delete {}".format(fil.absolute_url()))
    if doit and i % 1000 == 0:
        logger.warn('Commit done on count {}'.format(i))
        transaction.commit()

logger.warn('Deleted {} files'.format(i))

if doit:
    transaction.commit()
    logger.warn('Commit done')
