# -*- coding: utf-8 -*-

from DateTime import DateTime
from imio.helpers.security import setup_logger
from zope.annotation.interfaces import IAnnotations

import csv
import json
import logging
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
    "dv_size (MB)": 0,
    "file_size (MB)": 0,
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
    key = (parent_portal_type, portal_type)

    if key not in stats:
        stats[key] = STATS_TEMPLATE.copy()
    stats[key]["total_count"] += 1

    if "blob_files" not in annot:
        continue

    dv_sizes = dict()
    for k, v in annot["blob_files"].items():
        size = k.split("/")[0] + " (bytes)"
        dv_sizes[size] = dv_sizes.get(size, 0) + len(v.open().read())
    stats[key]["num_pages"] += annot.get("num_pages", 0)
    stats[key]["file_size (MB)"] += file.file.getSize()

    if annot.get("last_updated", "") == already_done:
        stats[key]["already_done_count"] += 1
        continue
    if annot.get("last_updated", "") == already_eml:
        stats[key]["already_eml_count"] += 1
        continue

    for size in ("small (bytes)", "normal (bytes)", "large (bytes)", "text (bytes)"):
        stats[key][size] += dv_sizes.get(size, 0)
        stats[key]["dv_size (MB)"] += dv_sizes.get(size, 0)

for v in stats.values():
    v["dv_size (MB)"] //= 1024 * 1024
    v["file_size (MB)"] //= 1024 * 1024

logger.info("Stats: {}".format(json.dumps({str(k): v for k, v in stats.items()}, indent=2, default=str)))

with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as temp_file:
    for k in stats:
        (parent_portal_type, portal_type) = k
        stats[k]["mail type"] = parent_portal_type
        stats[k]["file type"] = portal_type

    w = csv.DictWriter(
        temp_file,
        [
            "mail type",
            "file type",
            "total_count",
            "already_done_count",
            "already_eml_count",
            "num_pages",
            "small (bytes)",
            "normal (bytes)",
            "large (bytes)",
            "text (bytes)",
            "dv_size (MB)",
            "file_size (MB)",
        ],
    )
    w.writeheader()
    w.writerows(stats.values())

    temp_file_path = temp_file.name

logger.info("CSV file created at {}".format(temp_file_path))
