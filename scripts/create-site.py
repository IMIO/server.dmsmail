# -*- coding: utf-8 -*-
"""Creates an iA.Docs site (Plone 6): bin/instance1 run scripts/create-site.py [site_id] [profile]

profile: imio.dms.mail:default (empty site) or imio.dms.mail:examples (demo data, default)
"""
from AccessControl.SecurityManagement import newSecurityManager
from plone import api
from Products.CMFPlone.factory import addPloneSite
from Products.ExternalMethod.ExternalMethod import manage_addExternalMethod
from Testing.makerequest import makerequest
from zope.component.hooks import setSite

import sys
import transaction


args = [a for a in sys.argv[1:] if not a.endswith(".py") and not a.startswith("-")]
site_id = args[0] if args else "standard"
profile = args[1] if len(args) > 1 else "imio.dms.mail:examples"

app = makerequest(app)  # noqa: F821
if app.acl_users.getUserById("admin") is None:  # new database: the inituser file is only read by a started instance
    app.acl_users._doAddUser("admin", "admin", ["Manager"], [])
newSecurityManager(None, app.acl_users.getUserById("admin").__of__(app.acl_users))
if site_id in app.objectIds():
    sys.exit("Site '{}' already exists".format(site_id))

site = addPloneSite(
    app, site_id, title="iA.Docs", distribution_name="classic", default_language="fr", setup_content=False
)
setSite(site)
api.portal.set_registry_record("plone.available_languages", ["fr"])
api.portal.set_registry_record("plone.default_language", "fr")
# as imio.dms.mail testing layer: the setup modifies the front-page document
api.content.create(container=site, type="Document", id="front-page", title="Accueil")
site.setDefaultPage("front-page")
for mid, func in (
    ("import_scanned", "import_scanned"),
    ("import_scanned2", "import_scanned2"),
    ("create_main_file", "create_main_file"),
    ("activate_group_encoder", "activate_group_encoder"),
):
    manage_addExternalMethod(site, mid, mid, "imio.dms.mail.demo", func)
transaction.commit()
site.portal_setup.runAllImportStepsFromProfile("profile-{}".format(profile))
transaction.commit()
print("Site '{}' created with profile {}".format(site_id, profile))
