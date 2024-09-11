#!/bin/bash
return_code=0
/home/team/lotteh/venv/bin/python /home/team/lotteh/pam.py
return_code=$(($return_code + $?))
echo $return_code
if [ $return_code == 0 ]; then
    exit 0
else
    exit 1
fi
