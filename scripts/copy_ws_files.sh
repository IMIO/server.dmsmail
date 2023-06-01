#!/bin/bash
# files list is gotten from a query like this:
# select external_id, filepath from file where client_id = '081300' and type='COUR_E' and filepath is not null;

FILE=""
TODIR=""
usage () {
    echo "Usage: $0 files.txt"
    echo "First parameter is a file with lines like 'external_id,file_path' (mandatory)"
    echo "Second parameter is the target directory (optional)"
}
# We check the parameters
if [ "$1" != "" ]
then
    FILE=$1
else
    usage
    exit 3
fi
if [ ! -e "$FILE" ]; then
    echo "File '$FILE' doesn't exist"
    exit 3
fi
if [ "$2" != "" ]
then
    TODIR=$2
else
    TODIR=.
fi
if [ ! -d "$TODIR" ]; then
    echo "Folder '$TODIR' doesn't exist"
    exit 3
fi

while read line
do
    FPATH=`echo $line | cut -d ',' -f2`
    # echo $FPATH
    scp ws:$FPATH $TODIR
done < "$FILE"

