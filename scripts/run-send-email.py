# -*- coding: utf-8 -*-
from imio.helpers.emailer import create_html_email
from imio.helpers.emailer import get_mail_host
from imio.helpers.emailer import send_email
from imio.helpers.security import setup_logger
from imio.pyutils.system import stop

import argparse
import logging
import sys
import transaction


if 'app' not in locals() or 'obj' not in locals():
    stop("This script must be run via 'bin/instance -Oxxx run' !")

logger = logging.getLogger('run-send-email')
portal = obj  # noqa
setup_logger()

# Parameters check
args = sys.argv
if len(args) < 3 or args[1] != '-c' or not args[2].endswith('run-send-email.py'):
    stop("Arguments are not formatted as needed. Has the script been run via 'instance run'? "
         "Args are '{}'".format(args), logger=logger)
args.pop(1)  # remove -c
args.pop(1)  # remove script name
parser = argparse.ArgumentParser(description='Run send email test.')
parser.add_argument('-f', '--from', dest='sender', help='Sender')
parser.add_argument('-s', '--subject', dest='subject', help='Subject')
parser.add_argument('-d', '--doit', action='store_true', dest='doit', help='To commit and send email if queueing')
parser.add_argument('-i', '--immediate', action='store_true', dest='immediate', help='Send immediately')
parser.add_argument('-r', '--recipient', dest='recipients', action='append', default=[],
                    help='Recipient')
parser.add_argument('-c', '--cc', dest='ccs', action='append', default=[], help='Cc')
parser.add_argument('-b', '--bcc', dest='bccs', action='append', default=[], help='Bcc')
ns = parser.parse_args()

body = u"""Bonjour,
ceci est un mail de test.
Bien à vous."""
msg = create_html_email(body)
mailhost = get_mail_host(check=False)
sender = ns.sender
if not sender:
    sender = mailhost.smtp_uid
if not sender:
    sender = portal.email_from_address
if not sender:
    stop('No sender defined', logger=logger)
subject = ns.subject and ns.subject or u'Mail de test'
ret, error = send_email(msg, subject, sender, ns.recipients, mcc=ns.ccs, mbcc=ns.bccs, immediate=ns.immediate)
if ret:
    logger.info('Email sent')
else:
    logger.error('Your email has not been sent: {}.'.format(error))
if ns.doit:
    transaction.commit()
