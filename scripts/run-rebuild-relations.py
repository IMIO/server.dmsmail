# -*- coding: utf-8 -*-
from collective.relationhelpers.api import logger
from imio.dms.mail.relations_utils import rebuild_relations
from imio.helpers.security import setup_app

import logging


portal = obj  # noqa
setup_app(app, username='admin', logger=logger)  # noqa: F821 Otherwise, catalog search will fail
logger.setLevel(logging.INFO)
rebuild_relations(portal)
