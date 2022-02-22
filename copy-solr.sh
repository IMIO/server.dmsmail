#!/usr/bin/env bash

#set -ex

SOURCE_HOST="$(grep SOURCE_HOST= copy-data.sh|cut -d '=' -f 2 | tr -d '"')"
SOURCE_PATH="$(grep SOURCE_PATH= copy-data.sh|cut -d '=' -f 2 | tr -d '"')"
LOG="copy-solr.log"

if [ "$(whoami)" != "zope" ]; then
    echo "This script must be run as zope"
    exit -1
fi

if [ -f ${LOG} ]; then
    echo "It looks like this script has already been run."
    echo "If you want to run it again, please delete the '${LOG}' file."
    exit -1
fi

if [ ! -f bin/solr-start ]; then
    echo "It looks like bin/solr-start is not present in this directory."
    exit -1
fi

exec > >(tee -i ${LOG})
exec 2>&1

echo `date`
echo
echo "Copying solr files from ${SOURCE_HOST}:${SOURCE_PATH}/var/solr to var/ :"
rsync -e "ssh -o StrictHostKeyChecking=no" -avhP "${SOURCE_HOST}:${SOURCE_PATH}/var/solr" var/ --delete

echo
echo `date`
