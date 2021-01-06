FROM alpine

# set root user
USER root
s
# Install python, chromium and chromedriver
RUN apk update
RUN apk add py-pip
RUN apk add chromium postgresql-dev python3-dev gcc musl-dev
RUN apk add --no-cache chromium-chromedriver

# Install pillow (image library)
RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql \
    && pip install psycopg2 \
    && apk add jpeg-dev zlib-dev libjpeg \
    && pip install Pillow \
    && apk del build-deps

# Set directory to copy files into, and copy
WORKDIR /crawler
COPY . .

# Install selenium & co
RUN pip install --no-cache-dir -r requirements.txt
# run crawler with no gui (important, this only works if this is the case)
ENTRYPOINT ["python3", "main.py","--no_gui","true","--full", "true","--limit", "10","--no_driver","true","--region"]
CMD ["Berlin"]
# To run: docker run --name crawler image_name "location_name"
