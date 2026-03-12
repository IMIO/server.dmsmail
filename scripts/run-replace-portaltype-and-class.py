# -*- coding: utf-8 -*-
"""
Migrate some objects with mail_type='email' and a non-empty internal_number
to the new portal type.

Usage:
    BATCH=500 COMMIT=100 bin/instance1 run scripts/run-replace-portaltype-and-class.py
"""
from imio.helpers.batching import batch_get_keys
from imio.helpers.batching import batch_handle_key
from imio.helpers.batching import batch_hashed_filename
from imio.helpers.batching import batch_loop_else
from imio.helpers.batching import batch_skip_key
from imio.helpers.batching import can_delete_batch_files
from imio.helpers.security import setup_app
from imio.helpers.security import setup_logger
from imio.pyutils.batching import batch_delete_files
from plone.app.contenttypes.migration.dxmigration import migrate_base_class_to_new_class

import logging
import transaction


logger = logging.getLogger("replace-portaltype:")

portal = obj  # noqa
setup_logger()
setup_app(app)  # noqa

OLD_PORTAL_TYPE = "dmsincomingmail"
NEW_PORTAL_TYPE = "dmsincoming_email"
NEW_CLASS_NAME = "imio.dms.mail.dmsmail.ImioDmsIncomingMail"

pc = portal.portal_catalog
brains = pc.unrestrictedSearchResults(
    portal_type=["dmsincomingmail", "dmsincoming_email"],
    mail_type="email",
    # internal_number={'not': [None, '']},
    # sort_on='internal_number',
)
total = len(brains)
logger.info("Found %s objects to migrate", total)

pklfile = batch_hashed_filename("replace_portaltype.pkl")
batch_keys, config = batch_get_keys(pklfile, total, log=True)

for brain in brains:
    uid = brain.UID
    if batch_skip_key(uid, batch_keys, config):
        continue
    if brain.portal_type == NEW_PORTAL_TYPE:
        logger.debug("Already migrated: %s", brain.getPath())
    else:
        obj_inst = brain._unrestrictedGetObject()
        if "{}.{}".format(obj_inst.__class__.__module__, obj_inst.__class__.__name__) != NEW_CLASS_NAME:
            migrate_base_class_to_new_class(obj_inst, new_class_name=NEW_CLASS_NAME)
        if obj_inst.portal_type != NEW_PORTAL_TYPE:
            obj_inst.portal_type = NEW_PORTAL_TYPE
        obj_inst.reindexObject(idxs=["portal_type", "object_provides"])
        # logger.debug("Migrated: %s", brain.getPath())
    if batch_handle_key(uid, batch_keys, config):
        break
else:
    batch_loop_else(batch_keys, config)
    if not config["bn"]:
        # transaction.commit()
        logger.info("Migration complete, committed %s objects", config["lc"])

if can_delete_batch_files(batch_keys, config):
    batch_delete_files(batch_keys, config, rename=False)
    logger.info("Batch files deleted, migration fully complete")
