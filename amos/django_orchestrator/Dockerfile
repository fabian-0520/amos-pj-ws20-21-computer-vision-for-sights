FROM python:3.8
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/

ENV PYTHONUNBUFFERED 1
ENV PYTHONWRITEBYTECODE 1
ENV PYTHONPATH "/django_orchestrator"

EXPOSE 1337
CMD ["python", "manage.py", "runserver", "0.0.0.0:1337"]
