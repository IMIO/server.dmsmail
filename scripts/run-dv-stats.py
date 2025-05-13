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


STATS_TEMPLATE = {
    "total_count": 0,
    "already_done_count": 0,
    "already_eml_count": 0,
    "num_pages": 0,
    "small (bytes)": 0,
    "normal (bytes)": 0,
    "large (bytes)": 0,
    "text (bytes)": 0,
    "dv_size (KB)": 0,
    "file_size (KB)": 0,
}


already_done = DateTime("2010/01/01").ISO8601()  # when using image saying preview has been deleted
already_eml = DateTime("2011/01/01").ISO8601()  # when using image saying eml cannot be converted

portal = obj  # noqa
setup_logger()
logger = logging.getLogger("catalog:")

pc = portal.portal_catalog
brains = pc.unrestrictedSearchResults(portal_type=["dmsmainfile", "dmsommainfile", "dmsappendixfile"])

stats = {}
for brain in brains:
    file = brain.getObject()
    annot = IAnnotations(file).get("collective.documentviewer", "")
    portal_type = file.portal_type
    parent_portal_type = file.__parent__.portal_type

    if parent_portal_type not in stats:
        stats[parent_portal_type] = dict()
    if portal_type not in stats[parent_portal_type]:
        stats[parent_portal_type][portal_type] = STATS_TEMPLATE.copy()

    stats[parent_portal_type][portal_type]["total_count"] += 1

    if "blob_files" not in annot:
        continue

    dv_sizes = dict()
    for k, v in annot["blob_files"].items():
        size = k.split("/")[0] + " (bytes)"
        dv_sizes[size] = dv_sizes.get(size, 0) + len(v.open().read())
    stats[parent_portal_type][portal_type]["num_pages"] += annot.get("num_pages", 0)
    stats[parent_portal_type][portal_type]["file_size (KB)"] += file.file.getSize()

    if annot.get("last_updated", "") == already_done:
        stats[parent_portal_type][portal_type]["already_done_count"] += 1
        continue
    if annot.get("last_updated", "") == already_eml:
        stats[parent_portal_type][portal_type]["already_eml_count"] += 1
        continue

    for size in ("small (bytes)", "normal (bytes)", "large (bytes)", "text (bytes)"):
        stats[parent_portal_type][portal_type][size] += dv_sizes.get(size, 0)
        stats[parent_portal_type][portal_type]["dv_size (KB)"] += dv_sizes.get(size, 0)

for parent in stats.values():
    for file_k, file in parent.items():
        file["dv_size (KB)"] //= 1024
        file["file_size (KB)"] //= 1024

logger.info("Stats: {}".format(json.dumps(stats, indent=2)))

with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as temp_file:
    json.dump(stats, temp_file, indent=2)
    temp_file_path = temp_file.name
logger.info("Stats JSON file created at {}".format(temp_file_path))
