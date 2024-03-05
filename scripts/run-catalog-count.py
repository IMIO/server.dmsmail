# -*- coding: utf-8 -*-

from imio.helpers.security import setup_app
from imio.helpers.security import setup_logger
import logging

logger = logging.getLogger('catalog:')


portal = obj  # noqa
setup_logger()
setup_app(app)  # noqa
logger.info(len(portal.portal_catalog.unrestrictedSearchResults(path='/')))
