#!/bin/bash
svnparam="st"
if [ "$*" != "" ];
then
    svnparam=$*
else
    echo "!! You must pass a svn command as parameter : st, diff, up, ..."
    exit 0
fi

ScriptLocation="."
if [[ $0 == '/'* ]];
then
    ScriptLocation="`dirname $0`"
else
    ScriptLocation="`pwd`"/"`dirname $0`"
fi

# svn diff on all subdirectories of parts/svnproducts
find $ScriptLocation/../parts/svnproducts/ -maxdepth 1 -mindepth 1 -type d -name "??*" -print0 |xargs -0 svn $svnparam
