# -*- coding: utf-8 -*-
from imio.helpers.security import setup_app
from imio.helpers.security import setup_logger
from imio.pyutils.system import stop

import argparse
import logging
import sys
import transaction


logger = logging.getLogger("update_zope_admin_password")
setup_logger()
setup_app(app)  # noqa


def main(app, user_id):
    args = sys.argv
    if len(args) < 3 or args[1] != "-c" or not args[2].endswith("run-change-admin-password.py"):
        stop(
            "Arguments are not formatted as needed. Has the script been run via 'instance run'? "
            "Args are '{}'".format(args),
            logger=logger,
        )
    args.pop(1)  # remove -c
    args.pop(1)  # remove script name
    parser = argparse.ArgumentParser()

    parser.add_argument("new_password", type=str, help="New zope admin password for Plone instance")
    args = parser.parse_args()
    new_password = args.new_password

    acl_users = app.acl_users
    user = acl_users.getUser(user_id)
    if user:
        # update zope password
        users = acl_users.users
        users.updateUserPassword(user_id, new_password)
        logger.info("Well updated password")
        transaction.commit()
    else:
        logger.info("User {0} doesn't exists".format(user_id))


if __name__ == "__main__":
    user_id = "admin"
    main(app, user_id)  # noqa F821
