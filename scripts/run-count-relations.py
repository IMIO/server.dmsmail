# -*- coding: utf-8 -*-

from collective.relationhelpers.api import get_all_relations
from imio.helpers.security import setup_app
from imio.helpers.security import setup_logger
import logging

logger = logging.getLogger('relations:')


portal = obj  # noqa
setup_logger()
setup_app(app)  # noqa
logger.info(len(get_all_relations()))
