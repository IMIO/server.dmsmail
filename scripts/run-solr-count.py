# -*- coding: utf-8 -*-
"""Count documents in the solr collection configured in port.cfg.

Usage: bin/instance1 run scripts/run-solr-count.py ['<solr query>']
"""

from collective.solr.interfaces import ISearch
from collective.solr.interfaces import ISolrConnectionManager
from imio.helpers.security import setup_app
from imio.helpers.security import setup_logger
from zope.component import getUtility
from zope.component.hooks import setSite

import logging
import sys


logger = logging.getLogger('solr:')
portal = obj  # noqa
setup_logger()
setup_app(app)  # noqa
setSite(portal)  # needed to get the local solr utilities

query = len(sys.argv) > 3 and sys.argv[3] or '*:*'
conn = getUtility(ISolrConnectionManager).getConnection()
if conn is None:
    logger.error('solr is not active in the registry (collective.solr.active)')
else:
    logger.info('collection %s%s', conn.host, conn.solrBase)
    results = getUtility(ISearch)(query, rows=1)
    logger.info('%s => %d', query, results.actual_result_count)
