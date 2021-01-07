FROM python:3.8

WORKDIR /django_orchestrator

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENV PYTHONUNBUFFERED 1
ENV PYTHONWRITEBYTECODE 1
ENV PYTHONPATH "/django_orchestrator"

EXPOSE 8002
CMD ["python", "manage.py", "runserver", "0.0.0.0:8002"]
