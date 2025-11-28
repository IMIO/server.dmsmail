# -*- coding: utf-8 -*-
from imio.helpers.security import setup_logger
from imio.pyutils.system import stop
from plone.namedfile.file import NamedBlobFile
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import safe_unicode
from zope.lifecycleevent import modified

import argparse
import logging
import os
import requests
import sys
import transaction


if "app" not in locals() or "obj" not in locals():
    stop("This script must be run via 'bin/instance -Oxxx run' !")

logger = logging.getLogger("run")
portal = obj  # noqa
setup_logger()
portal_path = "/".join(portal.getPhysicalPath())

# Parameters check
args = sys.argv
if len(args) < 3 or args[1] != "-c" or not args[2].endswith("run-copy-missing-blobs.py"):
    stop(
        "Arguments are not formatted as needed. Has the script been run via 'instance run'? "
        "Args are '{}'".format(args),
        logger=logger,
    )
args.pop(1)  # remove -c
args.pop(1)  # remove script name

parser = argparse.ArgumentParser(
    description="Copy missing blobs from another site via RestAPI.",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="Examples:\n"
           "bin/instance1 -O run scripts/run-copy-missing-blobs.py "
           "-s https://demo-docs.imio.be -f odt_file -sp /templates "
           "-pt ConfigurablePODTemplate,MailingLoopTemplate,StyleTemplate,SubTemplate,DashboardPODTemplate "
           "-u  -p\n"
)
parser.add_argument("-s", "--source-url", required=True, help="Source site URL (e.g. https://source.example.com)")
parser.add_argument("-u", "--username", required=True, help="Username for authentication on source site")
parser.add_argument("-p", "--password", required=True, help="Password for authentication on source site")
parser.add_argument("-pf", "--paths-file", help="File containing list of paths (one per line)")
parser.add_argument("-f", "--field-name", default="file", help="Field name containing the blob (default: file)")
parser.add_argument("-sp", "--search-path", help="Base path to search for objects (e.g. /templates)")
parser.add_argument("-pt", "--portal-types", help="Comma-separated list of portal types to search (e.g. File,Image)")
parser.add_argument("-dr", "--dry-run", action="store_true", help="Do not commit changes")

ns = parser.parse_args()


def find_objects_by_criteria(base_path, portal_types):
    """Find objects by path and portal types using catalog."""
    from Products.CMFCore.utils import getToolByName

    catalog = getToolByName(portal, "portal_catalog")

    query = {"path": {"query": base_path}}
    if portal_types:
        types_list = [pt.strip() for pt in portal_types.split(",")]
        query["portal_type"] = types_list

    logger.info("Searching with query: {}".format(query))
    brains = catalog.unrestrictedSearchResults(**query)
    logger.info("Found {} objects in catalog".format(len(brains)))

    paths = []
    for brain in brains:
        obj = brain.getObject()
        if not base_hasattr(obj, ns.field_name):
            logger.warning("Object {} does not have field '{}'".format(brain.getPath(), ns.field_name))
            continue
        paths.append(brain.getPath())
    return paths


# Get paths either from file or by searching
if ns.paths_file:
    # Read paths from file
    try:
        with open(ns.paths_file, "r") as f:
            paths = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
    except IOError as e:
        stop("Cannot read paths file '{}': {}".format(ns.paths_file, e), logger=logger)

    if not paths:
        stop("No paths found in file '{}'".format(ns.paths_file), logger=logger)
elif not ns.search_path and not ns.portal_types:
    stop("Must pass at least --search-path or --portal-types to search for objects", logger=logger)
else:
    # Find objects by search criteria
    if ns.search_path:
        ns.search_path = ns.search_path.lstrip("/")
    paths = find_objects_by_criteria(os.path.join(portal_path, ns.search_path), ns.portal_types)
    if not paths:
        stop("No objects found matching search criteria", logger=logger)

logger.info("Found {} paths to process".format(len(paths)))
logger.info("Source site: {}".format(ns.source_url))
logger.info("Dry run: {}".format(ns.dry_run))

# Setup session with authentication
session = requests.Session()
session.auth = (ns.username, ns.password)
session.headers.update(
    {
        "Accept": "application/json",
    }
)

source_url = ns.source_url.rstrip("/")
processed = 0
success = 0
errors = 0


def fetch_blob_from_source(path, field_name):
    """Fetch blob data from source site via RestAPI."""
    url = "{}/{}/@@download/{}".format(source_url, path.lstrip("/"), field_name)
    logger.info("Fetching from: {}".format(url))

    try:
        response = session.get(url, timeout=60)
        if response.status_code == 200:
            return response.content, response.headers.get("Content-Type", "application/octet-stream")
        else:
            logger.error("Failed to fetch blob: HTTP {}".format(response.status_code))
            return None, None
    except Exception as e:
        logger.error("Exception while fetching blob: {}".format(e))
        return None, None


def get_filename_from_source(path):
    """Get filename from source object metadata."""
    url = "{}/{}".format(source_url, path.lstrip("/"))

    try:
        response = session.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            field_data = data.get(ns.field_name, {})
            if isinstance(field_data, dict):
                return field_data.get("filename", "downloaded_file")
            return "downloaded_file"
        else:
            return "downloaded_file"
    except Exception as e:
        logger.warning("Cannot get filename from source: {}".format(e))
        return "downloaded_file"


def copy_blob_to_object(obj, blob_data, content_type, filename):
    """Copy blob data to target object."""
    named_blob = NamedBlobFile(data=blob_data, contentType=content_type, filename=safe_unicode(filename))
    setattr(obj, ns.field_name, named_blob)
    modified(obj)


# import ipdb; ipdb.set_trace()  # noqa
for i, path in enumerate(paths, 1):
    logger.info("Processing [{}/{}]: {}".format(i, len(paths), path))

    processed += 1
    rel_path = path[len(portal_path) + 1:] if path.startswith(portal_path) else path
    # Get target object
    target_obj = portal.unrestrictedTraverse(path)
    if target_obj is None:
        logger.error("Target object not found at path: {}".format(path))
        errors += 1
        continue

    # Check if blob already exists
    existing_blob = getattr(target_obj, ns.field_name, None)
    if not existing_blob or not isinstance(existing_blob, NamedBlobFile):
        logger.warning("Field '{}' is not a NamedBlobFile on object {}".format(ns.field_name, path))
        errors += 1
        continue

    # filename = get_filename_from_source(path)
    filename = existing_blob.filename

    blob_data, content_type = fetch_blob_from_source(rel_path, ns.field_name)

    if blob_data is None:
        logger.error("Failed to fetch blob from source")
        errors += 1
        continue

    logger.info("Fetched blob: {} bytes, content-type: {}".format(len(blob_data), content_type))

    # Copy blob to target object
    try:
        copy_blob_to_object(target_obj, blob_data, content_type, filename)
        success += 1
    except Exception as e:
        logger.error("Error copying blob: {}".format(e))
        errors += 1

if not ns.dry_run and success > 0:
    transaction.commit()

# Summary
logger.info("")
logger.info("Total processed: {}".format(processed))
logger.info("Success: {}".format(success))
logger.info("Errors: {}".format(errors))
logger.info("Dry run: {}".format(ns.dry_run))
