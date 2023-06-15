# -*- coding: utf-8 -*-

from imio.helpers.security import setup_logger
from imio.pyutils.system import error
from imio.pyutils.system import verbose
from plone import api
import sys
import transaction


portal = obj  # noqa
setup_logger()
# Parameters check
if len(sys.argv) < 4 or not sys.argv[2].endswith('/run-change-ws-password.py'):
    error("Inconsistent or unexpected args len: %s" % sys.argv)
    sys.exit(1)

new_password = sys.argv[3]
prefix = 'imio.pm.wsclient.browser.settings.IWS4PMClientSettings'
if not api.portal.get_registry_record('{}.pm_url'.format(prefix), default=False):
    verbose("Password not set")
    sys.exit(0)
gen_act = api.portal.get_registry_record('{}.generated_actions'.format(prefix))
if gen_act and gen_act[0].get('permissions') and gen_act[0]['permissions'] != 'Modify view template':
    # activated
    api.portal.set_registry_record('{}.pm_password'.format(prefix), new_password)
    verbose("Password changed")
    transaction.commit()
else:
    verbose("Password not set")
