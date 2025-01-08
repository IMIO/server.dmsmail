# -*- coding: utf-8 -*-
from datetime import datetime
from email.header import decode_header
from imio.dms.mail import BLDT_DIR
# from imio.helpers.emailer import get_mail_host
from imio.helpers.security import setup_logger
from imio.pyutils.system import read_dictcsv
from imio.pyutils.system import read_dir
from imio.pyutils.system import stop
from operator import itemgetter

import argparse
import csv
import email
import logging
import os.path
import re
import shutil
import sys


# import transaction


if 'app' not in locals() or 'obj' not in locals():
    stop("This script must be run via 'bin/instance -Oxxx run' !")

logger = logging.getLogger('run-mailqueue')
portal = obj  # noqa
setup_logger()
mq_dir = os.path.join(BLDT_DIR, 'mailqueue')
new_dir = os.path.join(mq_dir, 'new')
bck_dir = os.path.join(mq_dir, 'backup')
file_pat = r'^\.(rejected|sending)-(.+)'
csv_file = os.path.join(mq_dir, 'mails.csv')
dt_format = "%Y-%m-%d,%H:%M"

# Parameters check
args = sys.argv
if len(args) < 3 or args[1] != '-c' or not args[2].endswith('run-mailqueue.py'):
    stop("Arguments are not formatted as needed. Has the script been run via 'instance run'? "
         "Args are '{}'".format(args), logger=logger)
args.pop(1)  # remove -c
args.pop(1)  # remove script name


def valid_date(s):
    try:
        return datetime.strptime(s, dt_format)
    except ValueError:
        raise argparse.ArgumentTypeError("Not a valid date with format '{}' : '{}'.".format(dt_format, s))


parser = argparse.ArgumentParser(description='Run mailqueue handling.')
parser.add_argument('-f', '--from', dest='f_date', type=valid_date, help='From date ({})'.format(dt_format))
# parser.add_argument('-i', '--immediate', action='store_true', dest='immediate', help='Send immediately')
# parser.add_argument('-r', '--recipient', dest='recipients', action='append', default=[],
#                     help='Recipient')
ns = parser.parse_args()
# mailhost = get_mail_host(check=False)

if not os.path.exists(mq_dir):
    stop("No mailqueue directory found at '{}'".format(mq_dir), logger=logger)

files = read_dir(new_dir, only_files=True)
if files and not os.path.exists(bck_dir):
    os.makedirs(bck_dir)
    logger.info("Created backup directory '{}'".format(bck_dir))

files_t = []
for fil in files:
    prefix = ""
    filename = fil
    if fil.startswith("."):
        match = re.match(file_pat, fil)
        if not match:
            stop("Prefix not found for file '{}'".format(fil), logger=logger)
        else:
            prefix = match.group(1)
            filename = match.group(2)
    parts = filename.split('.')
    time_dt = datetime.fromtimestamp(float('.'.join(parts[0:2])))
    files_t.append((fil, time_dt, prefix, filename))

files_t.sort(key=itemgetter(1))


def decode_header_value(header_value):
    decoded_values = decode_header(header_value)
    result = []
    for value, encoding in decoded_values:
        if isinstance(value, bytes) and encoding:
            value = value.decode(encoding)
        result.append(value)
    return ''.join(result)


files_infos = {}
fieldnames = ["fn", "prefix", "from", "to", "subject", "date"]

if os.path.exists(csv_file):
    error, csv_lines = read_dictcsv(csv_file, fieldnames=fieldnames, skip_lines=1, ln_key="_ln")
    if error:
        stop("Error reading csv file '{}' : {}".format(csv_file, error), logger=logger)
    for csv_line in csv_lines:
        fn = csv_line.pop("fn")
        files_infos[fn] = csv_line

csvfp = open(csv_file, 'w')
writer = csv.DictWriter(csvfp, fieldnames=fieldnames, dialect="excel")
writer.writeheader()

for fil, mod_t, prefix, filename in files_t:
    logger.info("Processing file '{}'".format(fil))
    fp = os.path.join(new_dir, fil)
    bfp = os.path.join(bck_dir, fil)
    f_i = files_infos.setdefault(filename, {"prefix": prefix, "date": mod_t.strftime("%Y-%m-%d %H:%M:%S")})
    # backup file
    if not os.path.exists(bfp):
        shutil.copy(fp, bfp)
        logger.info("Backed up file '{}'".format(fil))
    if prefix and ns.f_date and mod_t > ns.f_date:
        os.rename(fp, os.path.join(new_dir, filename))
        logger.info("Renamed file '{}'".format(fil))
    # extract mail infos
    if "from" not in f_i:
        with open(fp) as f_p:
            mail = email.message_from_file(f_p)
        f_i["from"] = mail.get("from")
        f_i["to"] = mail.get("to")
        f_i["subject"] = decode_header_value(mail.get("subject")).encode("utf-8")
    elif "_ln" in f_i:
        del f_i["_ln"]

# write infos to csv
logger.info("Writing infos to '{}'".format(csv_file))
for fn in files_infos:
    infos = files_infos[fn]
    infos["fn"] = fn
    writer.writerow(infos)
csvfp.close()
