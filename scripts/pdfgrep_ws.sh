#!/bin/bash
# files list is gotten from a query like this:
# \copy (select external_id, filepath, date from file where client_id = '081300' and type='COUR_E' and filepath is not null order by external_id) To '~/test.csv' CSV;

FILE=""
PAT=""
usage () {
    echo "Usage: $0 files.txt"
    echo "First parameter is a file with lines like 'external_id,file_path' (mandatory)"
    echo "Second parameter is the pattern"
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
    PAT=$2
else
    usage
    exit 3
fi

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

