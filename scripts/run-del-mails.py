# -*- coding: utf-8 -*-
from Acquisition import aq_inner  # noqa
from Acquisition import aq_parent  # noqa
from plone import api
from z3c.relationfield.event import removeRelations

import logging
import os
import sys
import transaction

# MUST BE TESTED AGAIN !!

portal = obj  # noqa
logger = logging.getLogger('del mails')
types = ['dmsincomingmail', 'dmsincoming_email', 'dmsoutgoingmail']
doit = False
if sys.argv[-1] == 'doit':
    doit = True
batch_value = int(os.getenv('BATCH', '0'))
# deactivate versioning
pr = portal.portal_repository
for typ in types:
    for pol_id in (u'at_edit_autoversion', u'version_on_revert'):
        pr.removePolicyFromContentType(typ, pol_id)
pr.setVersionableContentTypes([typ for typ in list(pr.getVersionableContentTypes()) if typ not in types])

pc = portal.portal_catalog
brains = pc.unrestrictedSearchResults(portal_type=types, sort_on='path')
count = 0
old_parent = None

for brain in brains:
    if brain.id == 'test_creation_modele':
        continue
    if batch_value and count > batch_value:  # so it is possible to run this step partially
        break
    bpath = os.path.dirname(brain.getPath())
    mail = brain.getObject()
    parent = aq_parent(aq_inner(mail))
    if old_parent and parent != old_parent and old_parent.id not in ('incoming-mail', 'outgoing-mail'):
        if not old_parent.objectIds():
            # logger.warn("Delete folder '{}'".format(old_parent.absolute_url()))
            api.content.delete(obj=old_parent, check_linkintegrity=False)
    old_parent = parent
    removeRelations(mail, None)  # to avoid possible error when deleting parent
    # logger.warn("Delete mail '{}'".format(mail.absolute_url()))
    api.content.delete(obj=mail, check_linkintegrity=False)
    count += 1

if old_parent and not old_parent.objectIds() and old_parent.id not in ('incoming-mail', 'outgoing-mail'):
    # logger.warn("Delete folder '{}'".format(old_parent.absolute_url()))
    api.content.delete(obj=old_parent, check_linkintegrity=False)

logger.warn('Will delete {} mails'.format(count))

if doit:
    transaction.commit()
    logger.warn('Commit done')
