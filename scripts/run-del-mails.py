# -*- coding: utf-8 -*-
from Acquisition import aq_inner  # noqa
from Acquisition import aq_parent  # noqa
from plone import api
from z3c.relationfield.event import removeRelations

import logging
import os
import sys
import transaction


portal = obj  # noqa
logger = logging.getLogger('del files')
types = ['dmsincomingmail', 'dmsincoming_email', 'dmsoutgoingmail']
doit = False
if sys.argv[-1] == 'doit':
    doit = True

pc = portal.portal_catalog
brains = pc.unrestrictedSearchResults(portal_type=types, sort_on='path')
count = 0
old_parent = None

for brain in brains:
    if brain.id == 'test_creation_modele':
        continue
    bpath = os.path.dirname(brain.getPath())
    mail = brain.getObject()
    parent = aq_parent(aq_inner(mail))
    if old_parent and parent != old_parent:
        if not old_parent.objectIds():
            # logger.warn("Delete folder '{}'".format(old_parent.absolute_url()))
            api.content.delete(obj=old_parent, check_linkintegrity=False)
    old_parent = parent
    removeRelations(mail, None)  # to avoid possible error when deleting parent
    # logger.warn("Delete mail '{}'".format(mail.absolute_url()))
    api.content.delete(obj=mail, check_linkintegrity=False)
    count += 1
else:
    if old_parent and not old_parent.objectIds():
        # logger.warn("Delete folder '{}'".format(old_parent.absolute_url()))
        api.content.delete(obj=old_parent, check_linkintegrity=False)

logger.warn('Will delete {} mails'.format(count))

if doit:
    transaction.commit()
    logger.warn('Commit done')
