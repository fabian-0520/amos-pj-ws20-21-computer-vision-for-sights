FROM nvcr.io/nvidia/pytorch:20.12-py3

# Install linux packages
RUN apt update && apt install -y screen libgl1-mesa-glx

# Install python dependencies
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

# Create working directory
RUN mkdir -p /usr/src/yolov5
WORKDIR /usr/src/yolov5

# Copy contents
COPY . /usr/src/yolov5

# Download weights initially
RUN python3 -c "from models import *; \
from utils import google_utils; \
google_utils.attempt_download('weights/yolov5s.pt')"

# Fetch images, store and generate config .yml
CMD python3 -c "from trainer_endpoint import persist_training_data; persist_training_data()"

# Run training
CMD ["python3", "train.py", "--epochs", "1", "--data", "sight_training_config.yaml", "--weights", "yolov5s.pt"]

# Run strip optimizer to get a temporary weights file
CMD python3 -c "from utils.general import *; strip_optimizer('runs/train/exp0_*/weights/best.pt', 'tmp.pt')"

# Load weights into database
CMD python3 -c "from trainer_endpoint import upload_trained_model; upload_trained_model()"

# Cleanup after training for next container launch
CMD python3 -c "from trainer_endpoint import cleanup; cleanup()"
