# -*- coding: utf-8 -*-
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import safe_callable

import logging
import os
import pickle
import sys
import transaction


portal = obj  # noqa
logger = logging.getLogger('ob')
logger.setLevel(logging.INFO)
run_part = os.getenv('FUNC_PART', '')
parts = os.getenv('PARTS', '')
batch_value = int(os.getenv('BATCH', '0'))
commit_value = int(os.getenv('COMMIT', '0'))
doit = False
if sys.argv[-1] == 'doit':
    doit = True
paths = {}
filename = 'to_index.pickle'
# load pickle file to have already handled mails
if os.path.exists(filename):
    logger.info('Loading pickle file')
    with open(filename, 'rb') as fh:
        paths = pickle.load(fh)


def indexObject(obj, path):
    __traceback_info__ = path
    if base_hasattr(obj, 'indexObject') and safe_callable(obj.indexObject):
        try:
            obj.indexObject()
        except TypeError:
            # Catalogs have 'indexObject' as well, but they
            # take different args, and will fail
            pass


def log(obj, path):
    logger.warning(path)


def store(obj, path):
    paths[path] = {'t': obj.portal_type, 'i': False}


pc = portal.portal_catalog
# clear
if '1' in parts:
    logger.info('Clearing catalog')
    pc.manage_catalogClear()
# index root items
if '2' in parts:
    logger.info('Reindexing root items')
    portal.ZopeFindAndApply(portal, search_sub=False, apply_func=indexObject)
    # portal.ZopeFindAndApply(portal, search_sub=False, apply_func=log)
# get root items
res = portal.ZopeFindAndApply(portal, search_sub=False)
# index all except root mail folders
if '3' in parts:
    logger.info('Reindexing all except root mail folders')
    for path, obj in res:
        if path not in ('incoming-mail', 'outgoing-mail'):
            portal.ZopeFindAndApply(obj, search_sub=True, apply_func=indexObject, pre=path)
    if doit:
        transaction.commit()
# store root mail folders content
if '4' in parts:
    logger.info('Storing mails paths in pickle file')
    for path, obj in res:
        if path in ('incoming-mail', 'outgoing-mail'):
            portal.ZopeFindAndApply(obj, search_sub=True, apply_func=store, pre=path)
    with open(filename, 'wb') as fh:
        pickle.dump(paths, fh)


def index_paths(excluded=[]):
    count = 0
    for path in sorted(paths.keys()):
        if paths[path]['i'] or paths[path]['t'] in excluded:
            continue
        count += 1
        if batch_value and count >= batch_value:
            break
        # logger.warning(path)
        obj = portal.unrestrictedTraverse(path)
        obj.reindexObject()
        paths[path]['i'] = True
        if doit and commit_value and count % commit_value == 0:
            logger.info("Committing {} '{}'".format(count, path))
            transaction.commit()


# index all but files
if '5' in parts and 'a' == run_part:
    logger.info('Reindexing all mails but files')
    index_paths(excluded=['dmsmainfile', 'dmsommainfile', 'dmsappendixfile'])

# index files
if '6' in parts and 'b' == run_part:
    logger.info('Reindexing all mail files')
    index_paths()

if doit:
    transaction.commit()
    logger.warn('Commit done')
