FROM python:3.8

WORKDIR /image_labelling_service

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENV PYTHONUNBUFFERED 1
ENV PYTHONWRITEBYTECODE 1
ENV PYTHONPATH "/image_labelling_service"

EXPOSE 7331
CMD ["python", "manage.py", "runserver", "0.0.0.0:7331"]
