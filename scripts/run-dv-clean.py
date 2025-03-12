# -*- coding: utf-8 -*-

from imio.helpers.security import setup_logger

import logging


portal = obj  # noqa
setup_logger()
logger = logging.getLogger("dv_clean:")

portal.unrestrictedTraverse("@@various-utils/dv_images_clean")()

logger.info("End of dv_clean script")
