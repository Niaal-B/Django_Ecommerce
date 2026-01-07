#!/usr/bin/env bash
# Startup script for Render - runs migrations then starts gunicorn

set -o errexit  # Exit on error

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Setting up Django Site..."
python setup_site.py || echo "Site setup failed or already exists"

echo "Starting gunicorn..."
exec gunicorn Evara.wsgi:application --bind 0.0.0.0:$PORT --timeout 120

