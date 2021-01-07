FROM python:3.9

WORKDIR /data_mart_refresher

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
ENV PYTHONPATH "/data_mart_refresher"
CMD [ "python", "./cron_jobs/main.py" ]
