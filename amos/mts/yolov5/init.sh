#!/bin/bash

# Download images
python3 trainer_endpoint.py
# Start training
python3 train.py --epochs 1 --data sight_training_config.yaml --weights yolov5s.pt
# strip optimizer that reduces weights to tmp
python3 -c "from utils.general import *; strip_optimizer('runs/train/exp0_*/weights/best.pt', 'tmp.pt')"
# final clean up
python3 -c "from trainer_endpoint import cleanup; cleanup()"
