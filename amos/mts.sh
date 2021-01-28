#!/bin/bash

PGHOST=$1
PGPORT=$2
PGDATABASE=$3
PGUSER=$4
PGPASSWORD=$5
CITY=$6
EPOCHS=$7

nvidia-docker run --ipc=host --gpus all -e PGHOST=$PGHOST -e PGDATABASE=$PGDATABASE -e PGUSER=$PGUSER -e PGPORT=$PGPORT -e PGPASSWORD=$PGPASSWORD -e city=$CITY -e -it mts $EPOCHS
sleep 10
/sbin/shutdown -h now