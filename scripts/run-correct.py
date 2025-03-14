# -*- coding: utf-8 -*-

from imio.helpers.security import setup_app
from imio.helpers.security import setup_logger
from plone import api

import logging
import sys
import transaction


logger = logging.getLogger('run-correct:')


portal = obj  # noqa
setup_logger()
setup_app(app)  # noqa
routing_key = "imio.dms.mail.browser.settings.IImioDmsMailConfig.iemail_routing"
routing = api.portal.get_registry_record(routing_key, default=[]) or []
if not routing:
    logger.error("No routing found in registry")
    sys.exit(1)
dic0 = routing[0]
if dic0[u"tal_condition_2"]:
    dic0[u"user_value"] = u"_empty_"
    dic0[u"tal_condition_1"] = u"python: agent_id and 'encodeurs' in modules['imio.dms.mail.utils']." \
        u"current_user_groups_ids(userid=agent_id)"
    dic0[u"tal_condition_2"] = u""
    logger.info("Corrected routing")
    api.portal.set_registry_record(routing_key, routing)
    transaction.commit()
