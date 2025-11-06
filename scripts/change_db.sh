#!/bin/bash

CUR=''
if [ -e .db-version ]; then CUR=`cat .db-version`; fi
echo "CUR=$CUR"
NEW=''
DOIT=0
WRITE_NEW=0
usage () {
  echo "Usage: $0 current new"
  echo "First parameter is the name of the current db where files will be backuped"
  echo "Second parameter is the name of the new db gotten from backup"
  echo "Third parameter must be 1 to really apply changes"
}
# We check the parameters
if [ "$1" != "" ]; then if [ "$CUR" == "" ]; then CUR=$1; fi else usage; exit 3; fi
if [ "$2" != "" ]; then NEW=$2; else usage; exit 3; fi
if [ "$3" == "1" ]; then DOIT=1; fi

execute_cmd () {
  action=$1
  shift
  echo "+ $*" >&2
  if [ $action -eq 1 ] && [ -e "${!#}" ]; then
    echo "!! dest file '${!#}' already exists" >&2;
  fi
  if [ $DOIT -eq 1 ]; then
    "$@"
    if [ $? -ne 0 ] ; then
      echo "Error in previous command"
      exit $?
    fi
  fi
}
echo "NEW=$NEW"

#for path in var/filestorage/Data.fs var/blobstorage dt_csv_dir dt_files_dir data-transfer.cfg
for path in var/filestorage/Data.fs var/blobstorage dt_csv_dir dt_files_dir
do
  if [ -e "$path" ] || [ -L "$path" ]; then
    cmd=(mv $path $path.$CUR)
    execute_cmd 1 "${cmd[@]}"
  fi
  if [ -e "$path.$NEW" ] || [ -L "$path.$NEW" ]; then
    cmd=(mv $path.$NEW $path)
    execute_cmd 0 "${cmd[@]}"
    WRITE_NEW=1
  fi
done

if [ $WRITE_NEW -eq 1 ]; then
  echo "+ echo \"$NEW\" > .db-version" >&2;
  if [ $DOIT -eq 1 ]; then echo "$NEW" > .db-version; fi
fi
