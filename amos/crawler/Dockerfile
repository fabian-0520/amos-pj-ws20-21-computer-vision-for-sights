FROM alpine

# set root user
USER root

# Install python, chromium and chromedriver
RUN apk update
RUN apk add py-pip
RUN apk add chromium
RUN apk add --no-cache chromium-chromedriver

# Set directory to copy files into, and copy
WORKDIR /crawler
COPY . .

# Install selenium & co
RUN pip install --no-cache-dir -r requirements.txt

# run crawler with no gui (important, this only works if this is the case)
ENTRYPOINT ["python3", "main.py","--no_gui","true","--full", "true","--limit", "10","--no_driver","true","--region"]
CMD ["Berlin"]
# To run: docker run --name crawler image_name "location_name"
