#!/bin/bash

EPOCHS=$1

# Download images
python3 trainer_endpoint.py
# Start training
python3 train.py --epochs $EPOCHS --data sight_training_config.yaml --weights yolov5s.pt
# strip optimizer that reduces weights to tmp
python3 -c "from utils.general import *; strip_optimizer('runs/train/exp/weights/best.pt', 'tmp.pt')"
# upload the weights
python3 -c "from trainer_endpoint import upload_trained_model; upload_trained_model()"
# final clean up
python3 -c "from trainer_endpoint import cleanup; cleanup()"
