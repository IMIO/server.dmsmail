# -*- coding: utf-8 -*-

from plone import api
from plone.dexterity.interfaces import IDexterityContent
from profilehooks import timecall
portal = obj  # noqa

pc = portal.portal_catalog


@timecall()
def various():
    brains = pc.unrestrictedSearchResults(object_provides=IDexterityContent.__identifier__)
    print(len(brains))


@timecall()
def various2():
    brains = pc.unrestrictedSearchResults(portal_type=('dmsincomingmail', 'dmsoutgoingmail'))
    print(len(brains))


various2()
