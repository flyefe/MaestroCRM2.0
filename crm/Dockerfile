ARG PYTHON_VERSION=3.12-slim

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies.
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    pkg-config \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /code

WORKDIR /code

COPY requirements.txt /tmp/requirements.txt
RUN set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -rf /root/.cache/
COPY . /code

ENV SECRET_KEY "2qdsrzik75rxTdtDSYjy1wJfbj6zWzDiRCnpo4Sm5OA7zGrkCx"
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# CMD ["gunicorn","--bind",":8000","--workers","2","crm.wsgi"]
CMD ["sh", "-c", "python manage.py migrate && gunicorn --bind :8000 --workers 2 crm.wsgi"]

