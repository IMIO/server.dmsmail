#!/bin/bash

CUR=''
NEW=''
DOIT=0
usage () {
  echo "Usage: $0 current new"
  echo "First parameter is the name of the current db where files will be backuped"
  echo "Second parameter is the name of the new db gotten from backup"
}
# We check the parameters
if [ "$1" != "" ]; then CUR=$1; else usage; exit 3; fi
if [ "$2" != "" ]; then NEW=$2; else usage; exit 3; fi
if [ "$3" == "1" ]; then DOIT=1; fi

execute_cmd () {
  echo "+ $*" >&2
  if [ $DOIT -eq 1 ]; then
    "$@"
    if [ $? -ne 0 ] ; then
      echo "Error in previous command"
      exit $?
    fi
  fi
}
for path in var/filestorage/Data.fs var/blobstorage
do
  if [ -e "$path" ]; then
    cmd=(mv $path $path.$CUR)
    execute_cmd "${cmd[@]}"
  fi
  if [ -e "$path.$NEW" ]; then
    cmd=(mv $path.$NEW $path)
    execute_cmd "${cmd[@]}"
  fi
done

for path in dt_csv_dir dt_files_dir
do
  if [ -e "$path" ]; then
    cmd=(mv $path $path.$CUR)
    execute_cmd "${cmd[@]}"
  fi
  if [ -e "$path.$NEW" ]; then
    cmd=(mv $path.$NEW $path)
    execute_cmd "${cmd[@]}"
  fi
done

exit 0;

while read line
do
    FPATH=`echo $line | cut -d ',' -f2`;
    FPATH=${FPATH/\/srv\//\/srv\/webservice\/}
    # echo $FPATH
    if [[ "$FPATH" =~ .*\.(pdf|PDF) ]]
    then
        pdfgrep -iH --cache "$PAT" $FPATH;
    elif [[ "$FPATH" == *.tar ]]
    then
       tar tf "$FPATH" 2>/dev/null | while read -r FILE
       do
           if [[ "$FILE" =~ .*\.(pdf|PDF) ]]
           then
              tar -C /tmp -xf "$FPATH" "$FILE" 2>/dev/null;
              RES=`pdfgrep -iH "$PAT" "/tmp/$FILE"`
              if [ "$RES" != "" ]
              then
                echo "> FOUND in $FPATH: $RES"
              fi
	      rm -f "/tmp/$FILE"
	   fi
       done
    fi
done < "$FILE"

