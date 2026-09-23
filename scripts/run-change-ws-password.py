# -*- coding: utf-8 -*-

# from imio.helpers.security import setup_logger
from imio.pyutils.system import error
from imio.pyutils.system import verbose
from plone import api

import argparse
import sys
import transaction


portal = obj  # noqa
# setup_logger()

# Parameters check
s_args = sys.argv
if len(sys.argv) < 3 or not sys.argv[2].endswith("/run-change-ws-password.py"):
    error("Inconsistent or unexpected args len: %s" % sys.argv)
    sys.exit(1)
s_args.pop(1)  # remove -c
s_args.pop(1)  # remove script name
parser = argparse.ArgumentParser("bin/instance...")

parser.add_argument("new_password", type=str, help="New ws password")
parser.add_argument("-u", "--username", dest="username", help="Ws username. If given, match only this.")
parser.add_argument("-e", "--empty", dest="empty_only", action="store_true", help="Only add password if no password.")
parser.add_argument(
    "-a", "--already", dest="already_only", action="store_true", help="Only change password if already set."
)
args = parser.parse_args()
new_password = args.new_password

prefix = "imio.pm.wsclient.browser.settings.IWS4PMClientSettings"
if not api.portal.get_registry_record("{}.pm_url".format(prefix), default=False):
    verbose("wsclient not configured")
    sys.exit(0)

if args.empty_only and api.portal.get_registry_record("{}.pm_password".format(prefix), default=False):
    verbose("password already configured")
    sys.exit(0)

if args.already_only and not api.portal.get_registry_record("{}.pm_password".format(prefix), default=False):
    verbose("password not yet configured")
    sys.exit(0)

username = api.portal.get_registry_record("{}.pm_username".format(prefix), default="")
if args.username and (not username or username != args.username):
    verbose("don't change for username '{}' <> '{}'".format(username, args.username))
    sys.exit(0)

gen_act = api.portal.get_registry_record("{}.generated_actions".format(prefix))
if any(item.get("permissions") and item.get("permissions") != "Modify view template" for item in (gen_act or [])):
    # activated
    api.portal.set_registry_record("{}.pm_password".format(prefix), new_password)
    verbose("Password changed")
    transaction.commit()
else:
    verbose("no meeting activated ?")
