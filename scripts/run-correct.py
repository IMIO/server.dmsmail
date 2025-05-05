# -*- coding: utf-8 -*-

from imio.dms.mail.utils import get_dms_config
from imio.dms.mail.utils import set_dms_config
from imio.helpers.security import setup_app
from imio.helpers.security import setup_logger
from persistent.dict import PersistentDict

import logging
import transaction


logger = logging.getLogger('run-correct:')


portal = obj  # noqa
setup_logger()
setup_app(app)  # noqa

try:
    config = get_dms_config(["read_label_cron"])
    logger.info("Annotation already set")
except KeyError:
    set_dms_config(["read_label_cron"], PersistentDict())
    logger.info("Corrected annotation")
    transaction.commit()
