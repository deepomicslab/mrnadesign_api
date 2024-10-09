#!/bin/bash

trap "echo; echo 'script end'; exit" SIGINT
echo "if want end ,Ctrl + C"

module load GCCcore/11.2.0 GCC/11.2.0 Python/3.9.6

while true
do
    /apps/software/Python/3.9.6-GCCcore-11.2.0/bin/python /home/platform/phage_db/phage_api/manage.py crontab run 231c4f91aac3f6ddc1b3ad004b2fa754
    echo run contab
    sleep 1m
done