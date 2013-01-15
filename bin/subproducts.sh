#!/bin/bash
ScriptLocation="."
if [[ $0 == '/'* ]];
then ScriptLocation="`dirname $0`"
else ScriptLocation="`pwd`"/"`dirname $0`"
fi

# Installation of psycopg 2.0.13
cd $ScriptLocation/../subproducts
#tar -xvzf psycopg2-2.0.13.tar.gz
#cd psycopg2-2.0.13
#$ScriptLocation/python ./setup.py install
#cd ..
#rm -f -R psycopg2-2.0.13

