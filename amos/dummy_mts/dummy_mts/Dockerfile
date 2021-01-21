FROM nvcr.io/nvidia/pytorch:20.10-py3

# set the working directory in the container
WORKDIR /dummy_mts

# copy the content of the local src directory to the working directory
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENV PYTHONUNBUFFERED 1
ENV PYTHONWRITEBYTECODE 1

# command to run on container start
CMD [ "python", "detect.py" ]
