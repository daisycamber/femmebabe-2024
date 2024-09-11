#!/bin/bash
return_code=0
/home/team/lotteh/venv/bin/python /home/team/lotteh/logout.py
return_code=$(($return_code + $?))
echo $return_code
if [ $return_code == 1 ]; then
    exit 0
fi
if [ $return_code == 2 ]; then
    exit 1
fi
if [ $return_code == 0 ]; then
    exit 0
else
    exit 1
fi
