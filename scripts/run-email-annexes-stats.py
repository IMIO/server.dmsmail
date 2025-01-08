# -*- coding: utf-8 -*-

import csv
import logging
import tempfile


portal = obj  # noqa
logger = logging.getLogger('catalog:')

pc = portal.portal_catalog
brains = pc.unrestrictedSearchResults(portal_type='dmsincoming_email')

results = []
for brain in brains:
    email = brain.getObject()
    for appendix in email.objectValues():
        if appendix.portal_type != 'dmsappendixfile':
            continue
        results.append({
            "filename": appendix.file.filename,
            "extension": appendix.file.filename.split('.')[-1].encode("utf-8"),
            "size": appendix.file.getSize(),
            "url": appendix.absolute_url(),
        })

with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as temp_file:
    w = csv.DictWriter(temp_file, fieldnames=results[0].keys())
    w.writeheader()
    w.writerows(results)

    temp_file_path = temp_file.name

logger.info('CSV file created at {}'.format(temp_file_path))
