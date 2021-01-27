#!/bin/bash

PGHOST=$1
PGPORT=$2
PGDATABASE=$3
PGUSER=$4
PGPASSWORD=$5
CITY=$6

do nvidia-docker run --ipc=host --gpus all --name=training_container -e PGHOST=$PGHOST -e PGDATABASE=$PGDATABASE -e PGUSER=$PGUSER -e PGPORT=$PGPORT -e PGPASSWORD=$PGPASSWORD -e city=$CITY -it mts
sleep 1
do docker wait training_container
/sbin/shutdown -h now