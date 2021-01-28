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

# Start main script
ENTRYPOINT ["sh", "/usr/src/yolov5/init.sh"]