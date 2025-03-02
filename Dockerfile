FROM python:3.12-slim
LABEL authors="Undervis, Keyrdis"
ENV PYTHONUNBUFFERED=1
EXPOSE 8080

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

ENV DJANGO_SUPERUSER_USERNAME=admin
ENV DJANGO_SUPERUSER_EMAIL=example@mail.ru
ENV DJANGO_SUPERUSER_PASSWORD=1234


COPY . /tsm-backend
WORKDIR /tsm-backend

RUN ["python", "manage.py", "makemigrations"]
RUN ["python", "manage.py", "migrate"]
RUN ["python", "manage.py", "createsuperuser", "--noinput"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]