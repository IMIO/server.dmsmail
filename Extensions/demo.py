# -*- coding: utf-8 -*-
import os
from plone.namedfile.file import NamedBlobFile
from collective.dms.batchimport.utils import createDocument
from Products.CMFCore.utils import getToolByName
from datetime import datetime


def import_scanned(self):
    """
        Import some incoming mail for demo site
    """
    now = datetime.now().strftime('%Y%m%d %H:%M')
    path = '%s/../../Extensions' % os.environ.get('INSTANCE_HOME')
    docs = {
        '59.PDF':
        {
            'c': {'mail_type': 'courrier', 'file_title': 'IMIO010500000000001.pdf'},
            'f': {'scan_id': 'IMIO010500000000001', 'pages_number': '1', 'scan_date': now,
                  'scan_user': 'Opérateur', 'scanner': 'Ricola'}
        },
        '60.PDF':
        {
            'c': {'mail_type': 'courrier', 'file_title': 'IMIO010500000000002.pdf'},
            'f': {'scan_id': 'IMIO010500000000002', 'pages_number': '1', 'scan_date': now,
                  'scan_user': 'Opérateur', 'scanner': 'Ricola'}
        },
    }

    class Dummy(object):
        def __init__(self, context, request):
            self.context = context
            self.request = request

    portal = getToolByName(self, "portal_url").getPortalObject()
    folder = portal['incoming-mail']
    for doc in docs:
        with open('%s/%s' % (path, doc), 'rb') as fo:
            file_object = NamedBlobFile(fo.read(), filename=unicode(doc))

        (document, main_file) = createDocument(
            Dummy(portal, portal.REQUEST),
            folder,
            'dmsincomingmail',
            '',
            file_object,
            owner='scanner',
            metadata=docs[doc]['c'])
        for key, value in docs[doc]['f'].items():
            setattr(main_file, key, value)
        main_file.reindexObject(idxs=('scan_id',))
    return portal.REQUEST.response.redirect(folder.absolute_url())
