# -*- coding: utf-8 -*-
from imio.helpers.batching import batch_delete_files
from imio.helpers.batching import batch_get_keys
from imio.helpers.batching import batch_globally_finished
from imio.helpers.batching import batch_handle_key
from imio.helpers.batching import batch_hashed_filename
from imio.helpers.batching import batch_loop_else
from imio.helpers.batching import batch_skip_key
from imio.helpers.batching import can_delete_batch_files
from imio.helpers.batching import logger as m_logger
from plone import api

import logging


portal = obj  # noqa
m_logger.setLevel(logging.INFO)
logger = logging.getLogger('reindex')
logger.setLevel(logging.INFO)

portal_types = ['dmsincomingmail', 'dmsincoming_email']
pc = api.portal.get_tool('portal_catalog')
brains = pc.unrestrictedSearchResults(portal_type=portal_types, sort_on='created')

pklfile = batch_hashed_filename('dmsmail.run-reindex-security.pkl', (portal_types,))
batch_keys, batch_config = batch_get_keys(pklfile, loop_length=len(brains), log=True)

for brain in brains:
    key = brain.UID
    if batch_skip_key(key, batch_keys, batch_config):
        continue
    brain.getObject().reindexObjectSecurity()
    if batch_handle_key(key, batch_keys, batch_config):
        break
else:
    batch_loop_else(batch_keys, batch_config)

if can_delete_batch_files(batch_keys, batch_config):
    batch_delete_files(batch_keys, batch_config, log=True)
    logger.info('Reindexing finished')
elif batch_globally_finished(batch_keys, batch_config):
    logger.info('Reindexing finished')
else:
    logger.info('Reindexing to be continued')
