#!/bin/bash

trap "echo; echo 'script end'; exit" SIGINT
echo "if want end ,Ctrl + C"

module load GCCcore/11.2.0 GCC/11.2.0 Python/3.9.6

while true
do
    /apps/software/Python/3.9.6-GCCcore-11.2.0/bin/python /home/platform/project/mrnadesign_platform/mrnadesign_api/manage.py crontab run d6685bd8341b65d4546e7a8bf51a927b
    echo run contab
    sleep 1m
done