#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit  # Exit on error

echo "Building Django application..."

# Install dependencies
pip install --upgrade pip
pip install 'setuptools[legacy]>=65.5.0'  # Install setuptools with legacy support for pkg_resources
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate --noinput

echo "Build completed successfully!"

