# Use the official Python image.
FROM python:3.11-slim

# Set the working directory in the container.
WORKDIR /app

# Install system dependencies for MySQL and other tools.
RUN apt-get update && apt-get install -y \
    gcc \
    libmariadb-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container.
COPY requirements.txt .

# Install dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files into the container.
COPY . .

# Set environment variables for Django.
ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=crm.settings

# Collect static files
RUN python manage.py collectstatic --noinput

# Apply database migrations
RUN python manage.py migrate

# Run Django server (update to your project’s wsgi or asgi server for production).
CMD ["gunicorn", "crm.wsgi:application", "--bind", "0.0.0.0:8000"]