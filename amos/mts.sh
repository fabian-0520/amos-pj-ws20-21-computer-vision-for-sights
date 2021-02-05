#!/bin/bash

PGHOST=$1
PGPORT=$2
PGDATABASE=$3
PGUSER=$4
PGPASSWORD=$5
CITY=$6
EPOCHS=$7
MIN_IMAGE_NUMBER_PER_LABEL=$8

nvidia-docker run --ipc=host --gpus all -e PGHOST=$PGHOST -e PGDATABASE=$PGDATABASE -e PGUSER=$PGUSER -e PGPORT=$PGPORT -e PGPASSWORD=$PGPASSWORD -e city=$CITY -e -it mts $EPOCHS $MIN_IMAGE_NUMBER_PER_LABEL
sleep 10  # safe buffer
/sbin/shutdown -h now  # shut down EC2 instance afterwards