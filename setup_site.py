#!/usr/bin/env python
"""
Script to set up Django Site object for django-allauth.
Run this after migrations on Render: python setup_site.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Evara.settings')
django.setup()

from django.contrib.sites.models import Site

# Get the domain from environment or use a default
domain = os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'localhost:8000')
name = 'Evara E-commerce'

# Create or update the site
site, created = Site.objects.get_or_create(
    pk=1,
    defaults={'domain': domain, 'name': name}
)

if not created:
    # Update existing site
    site.domain = domain
    site.name = name
    site.save()
    print(f"Updated Site: {site.domain}")
else:
    print(f"Created Site: {site.domain}")

