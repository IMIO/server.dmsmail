# -*- coding: utf-8 -*-
"""Lists the POD expressions the 3.1 migration (collective.documentgenerator 16) replaces by ++REPLACED++.

Read-only. "stock" templates (unmodified imio.dms.mail ones) are reloaded by the migration.
"""
from collective.documentgenerator.content.pod_template import IPODTemplate
from collective.documentgenerator.search_replace.pod_template import SearchAndReplacePODTemplates
from imio.dms.mail.setuphandlers import list_templates
from Products.CMFPlone.utils import safe_unicode
from xml.sax.saxutils import unescape

import re
import transaction


# appy.pod.evaluator.Compromiser getBannedRex() and underscored (appy 1.0.22, absent from 3.0)
PATTERNS = (
    r'(?<![a-zA-Z0-9_.])(exec|eval|input|compile|getattr|setattr|hasattr|open|print|import|del|global)(?!\w)',
    r'__\w+__',
)

portal = obj  # noqa
stock_paths = [tup[1] for tup in list_templates()]
nb = 0
for brain in portal.portal_catalog.unrestrictedSearchResults(object_provides=IPODTemplate.__identifier__):
    pt = brain._unrestrictedGetObject()
    with SearchAndReplacePODTemplates([pt]) as search_replace:
        matches = search_replace.search('|'.join(PATTERNS), is_regex=True).get(pt.UID(), [])
    if not matches:
        continue
    nb += 1
    path = portal.portal_url.getRelativeContentURL(pt)
    stock = path in stock_paths and not pt.has_been_modified()
    print(u'{} "{}" [{}]'.format(path, safe_unicode(pt.Title()), stock and 'stock' or 'modified').encode('utf8'))
    for match in matches:
        expr = replaced = unescape(match.content, {'&quot;': '"', '&apos;': "'"})
        for pattern in PATTERNS:  # same order as documentgenerator Migrate_To_16
            replaced = re.sub(pattern, '++REPLACED++', replaced)
        for prefix, text in ((u'  - ', expr), (u'  > ', replaced)):
            print((prefix + safe_unicode(text).replace(u'\n', u'\n    ')).encode('utf8'))
print('{} POD template(s) with banned expressions'.format(nb))
transaction.abort()
