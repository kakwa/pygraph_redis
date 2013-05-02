#!/bin/sh

ret=0
cd `dirname $0`/tests
for i in `ls *.py`
do
    printf "\033[96m\n####### Starting $i ###########\n\033[97m"
    ./$i
    ret=$(( $? | $ret))
    if ! [ -z "$1" ]
    then
        printf "\033[96m\n####### Starting $i (python3) ###########\n\033[97m"
        python3 ./$i
        ret=$(( $? | $ret))
    fi
done
exit $ret
