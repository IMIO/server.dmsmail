# -*- coding: utf-8 -*-

from DateTime import DateTime
from imio.helpers.security import setup_logger
# from imio.helpers.xhtml import object_link
from imio.pyutils.utils import safe_encode
from zope.annotation.interfaces import IAnnotations

import csv
import json
import logging
import os
import tempfile


already_done = DateTime("2010/01/01").ISO8601()  # when using image saying preview has been deleted
already_eml = DateTime("2011/01/01").ISO8601()  # when using image saying eml cannot be converted

portal = obj  # noqa
setup_logger()
logger = logging.getLogger('catalog:')

pc = portal.portal_catalog
brains = pc.unrestrictedSearchResults(portal_type=['dmsmainfile', 'dmsommainfile', 'dmsappendixfile'])

results = []
stats = {
    'dmsmainfile': {
        'total_count': 0,
        'already_done_count': 0,
        'already_eml_count': 0,
        'num_pages': 0,
        'small (bytes)': 0,
        'normal (bytes)': 0,
        'large (bytes)': 0,
        'text (bytes)': 0,
    },
    'dmsommainfile': {
        'total_count': 0,
        'already_done_count': 0,
        'already_eml_count': 0,
        'num_pages': 0,
        'small (bytes)': 0,
        'normal (bytes)': 0,
        'large (bytes)': 0,
        'text (bytes)': 0,
    },
    'dmsappendixfile': {
        'total_count': 0,
        'already_done_count': 0,
        'already_eml_count': 0,
        'num_pages': 0,
        'small (bytes)': 0,
        'normal (bytes)': 0,
        'large (bytes)': 0,
        'text (bytes)': 0,
    },
}
for brain in brains:
    file = brain.getObject()
    annot = IAnnotations(file).get("collective.documentviewer", "")
    portal_type = file.portal_type
    stats[portal_type]['total_count'] += 1

    dv_sizes = dict()
    for k, v in annot['blob_files'].items():
        size = k.split('/')[0] + ' (bytes)'
        dv_sizes[size] = dv_sizes.get(size, 0) + len(v.open().read())
    stats[portal_type]['num_pages'] += annot.get("num_pages", 0)

    res = {
        "portal_type": portal_type,
        "title": safe_encode(file.Title()),
        "filename": safe_encode(file.file.filename),
        "extension": safe_encode(os.path.splitext(file.file.filename)[-1]),
        "file_size (bytes)": file.file.getSize(),
        "url": "{}/{}".format(file.absolute_url(), "view"),
        "num_pages": annot.get("num_pages", 0),
        "last_updated": annot.get("last_updated", ""),
    }
    res.update(dv_sizes)
    results.append(res)

    if annot.get("last_updated", "") == already_done:
        stats[portal_type]['already_done_count'] += 1
        continue
    if annot.get("last_updated", "") == already_eml:
        stats[portal_type]['already_eml_count'] += 1
        continue

    for size in ('small (bytes)', 'normal (bytes)', 'large (bytes)', 'text (bytes)'):
        stats[portal_type][size] += dv_sizes.get(size, 0)

logger.info("Results: {}".format(json.dumps(results, indent=2)))
logger.info("Stats: {}".format(json.dumps(stats, indent=2)))

if results:
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as temp_file:
        w = csv.DictWriter(temp_file, [
            "portal_type",
            "title",
            "filename",
            "extension",
            "file_size (bytes)",
            'small (bytes)',
            'normal (bytes)',
            'large (bytes)',
            'text (bytes)',
            "url",
            "num_pages",
            "last_updated",
        ])
        w.writeheader()
        w.writerows(results)

        temp_file_path = temp_file.name
    logger.info('Detailed CSV file created at {}'.format(temp_file_path))
else:
    logger.info('No results found')

with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
    json.dump(stats, temp_file, indent=2)
    temp_file_path = temp_file.name
logger.info('Stats JSON file created at {}'.format(temp_file_path))
