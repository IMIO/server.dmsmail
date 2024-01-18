# -*- coding: utf-8 -*-

portal = obj  # noqa

# portal.portal_setup.runImportStepFromProfile('collective.z3cform.select2:default', 'jsregistry')
portal.portal_setup.runImportStepFromProfile('imio.dms.mail:default', 'jsregistry')
for registry in ('portal_javascripts', 'portal_css'):
    tool = portal[registry]
    tool.cookResources()

import transaction
transaction.commit()
