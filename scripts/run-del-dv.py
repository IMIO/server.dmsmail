# -*- coding: utf-8 -*-
from imio.helpers.content import object_values
from zope.annotation import IAnnotations


import transaction


portal = obj  # noqa

types = ['dmsincomingmail', 'dmsincoming_email', 'dmsoutgoingmail']

pc = portal.portal_catalog
brains = pc.unrestrictedSearchResults(portal_type=types)
for brain in brains:
    mail = brain.getObject()
    for fobj in object_values(mail, ['DmsFile', 'DmsAppendixFile', 'ImioDmsFile']):
        annot = IAnnotations(fobj)
        if 'collective.documentviewer' not in annot:
            continue
        del annot['collective.documentviewer']

transaction.commit()
