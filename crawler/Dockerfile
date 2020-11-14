# alpine image with headless chrome
FROM zenika/alpine-chrome
USER root

RUN apk update

# Install python and chromedriver
RUN apk add py-pip
RUN apk add --no-cache chromium-chromedriver

WORKDIR /crawler

COPY . .

# start chrome with necessary flags
ENTRYPOINT ["chromium-browser", "--no-sandbox", "--remote-debugging-port=9222", "--headless", "--use-gl=swiftshader", "--disable-software-rasterizer", "--disable-dev-shm-usage"]

# Install selenium & co
RUN pip install -r requirements.txt

# run crawler
CMD ["python", "main.py"]