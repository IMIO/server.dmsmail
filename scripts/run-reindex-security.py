# -*- coding: utf-8 -*-
from imio.dms.mail.browser.settings import default_creating_group
from imio.dms.mail.utils import ensure_set_field
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

import argparse
import logging
import sys


portal = obj  # noqa
m_logger.setLevel(logging.INFO)
logger = logging.getLogger('reindex')
logger.setLevel(logging.INFO)

# Parameters check
s_args = sys.argv
if len(sys.argv) < 3 or not sys.argv[2].endswith("/run-reindex-security.py"):
    logger.error("Inconsistent or unexpected args len: %s" % sys.argv)
    sys.exit(1)
s_args.pop(1)  # remove -c
s_args.pop(1)  # remove script name
parser = argparse.ArgumentParser("bin/instance...")
parser.add_argument("-pt", "--portal-types", help="Comma-separated list of portal types to search (e.g. File,Image)",
                    default="dmsincomingmail,dmsincoming_email")
parser.add_argument("-ge", "--group-encoder", dest="group_encoder", action="store_true", help="Group encoder set.")

args = parser.parse_args()

portal_types = args.portal_types.split(',')
pc = api.portal.get_tool('portal_catalog')
brains = pc.unrestrictedSearchResults(portal_type=portal_types, sort_on='created')

pklfile = batch_hashed_filename('dmsmail.run-reindex-security.pkl', (portal_types,))
batch_keys, batch_config = batch_get_keys(pklfile, loop_length=len(brains), log=True)

for brain in brains:
    key = brain.UID
    if batch_skip_key(key, batch_keys, batch_config):
        continue
    obj = brain.getObject()
    if args.group_encoder and ensure_set_field(obj, "creating_group", default_creating_group(obj.getOwner())):
        obj.reindexObject(["assigned_group"])
    obj.reindexObjectSecurity()
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
