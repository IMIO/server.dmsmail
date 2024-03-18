# -*- coding: utf-8 -*-
from imio.helpers.batching import logger as m_logger
from imio.migrator.migrator import Migrator

import logging


portal = obj  # noqa
m_logger.setLevel(logging.INFO)
logger = logging.getLogger('reindex')
logger.setLevel(logging.INFO)

migrator = Migrator(portal.portal_setup)

if migrator.reindexIndexes(['labels'], update_metadata=False,
                           portal_types=['dmsincomingmail', 'dmsincoming_email']):
    logger.info('Reindexing finished')
else:
    logger.info('Reindexing to be continued')
