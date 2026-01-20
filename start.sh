#!/usr/bin/env bash
# Startup script for Render - runs migrations then starts gunicorn

set -o errexit  # Exit on error

echo "Running database migrations (with retry)..."
for i in {1..10}; do
  if python manage.py migrate --noinput; then
    break
  fi
  echo "Migrate failed (attempt $i/10). Waiting 3s and retrying..."
  sleep 3
done

echo "Setting up Django Site..."
python setup_site.py || echo "Site setup failed or already exists"

echo "Creating admin superuser..."
python manage.py create_admin || echo "Admin user creation failed or already exists"

echo "Starting gunicorn..."
exec gunicorn Evara.wsgi:application --bind 0.0.0.0:$PORT --timeout 120

