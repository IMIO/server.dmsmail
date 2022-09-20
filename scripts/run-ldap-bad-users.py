# -*- coding: utf-8 -*-

from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

portal = obj  # noqa
factory = getUtility(IVocabularyFactory, 'plone.principalsource.Users')
vocab = factory(portal)  # terms as username, userid, fullname
for term in vocab:
    try:
        unicode(term.token)
    except Exception:
        print(term.token)

