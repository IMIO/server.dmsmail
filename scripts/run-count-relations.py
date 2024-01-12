# -*- coding: utf-8 -*-

from AccessControl.SecurityManagement import newSecurityManager
from collective.relationhelpers.api import get_all_relations
from imio.helpers.security import setup_logger
from Testing import makerequest
from zope.globalrequest import setRequest
import logging

logger = logging.getLogger('relations:')


def setup_app(app, username='admin', logger=None):  # to be imported from imio.helpers.security
    acl_users = app.acl_users
    user = acl_users.getUser(username)
    if user:
        user = user.__of__(acl_users)
        newSecurityManager(None, user)
    elif logger:
        logger.error("Cannot find zope user '%s'" % username)
    app = makerequest.makerequest(app)
    # support plone.subrequest
    app.REQUEST['PARENTS'] = [app]
    setRequest(app.REQUEST)
    return user


portal = obj  # noqa
setup_logger()
setup_app(app)  # noqa
logger.info(len(get_all_relations()))
