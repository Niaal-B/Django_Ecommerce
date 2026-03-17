# 🛒 Evara - Django E-commerce Platform

<div align="center">

[![Django](https://img.shields.io/badge/Django-5.1.2-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**A modern, full-featured e-commerce web application built with Django**

[Features](#-features) • [Installation](#-installation) • [Configuration](#-configuration)

</div>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#️-tech-stack)
- [Getting Started](#-getting-started)
- [Installation](#-installation)
- [Configuration](#-configuration)





## 🎯 Overview

Evara is a comprehensive e-commerce platform that provides a complete shopping experience with user authentication, product catalog management, shopping cart functionality, order processing, and payment integration. Built with Django's robust framework, it offers both customer-facing features and an intuitive admin interface for managing products and orders.

### Key Highlights

- ✅ **User-friendly Interface** - Clean and modern design
- ✅ **Secure Authentication** - OTP verification and social login
- ✅ **Payment Integration** - Razorpay and COD support
- ✅ **Admin Dashboard** - Comprehensive management tools
- ✅ **Responsive Design** - Works on all devices
- ✅ **Production Ready** - Docker and cloud deployment support

## 🚀 Features

### 👤 User Features

#### Authentication & Security
- 🔐 User registration with OTP email verification
- 🔑 Secure login/logout functionality
- 🔄 Password reset via email
- 🌐 Social authentication (Google OAuth2)
- ✅ Email-based account verification

#### Shopping Experience
- 🛍️ Browse products by categories
- 🔍 Advanced product search and filtering
- 📸 Product details with multiple images
- 📏 Size variants and stock management
- 🛒 Shopping cart with real-time updates
- ❤️ Wishlist functionality
- 💰 Special offers and discount management

#### Order Management
- 📝 Secure checkout process
- 📦 Order history and tracking
- 📍 Multiple address management
- 📧 Order confirmation emails
- 🧾 Invoice generation (PDF)

#### Payment Options
- 💳 Razorpay payment gateway integration
- 💵 Cash on Delivery (COD) support
- 🔒 Secure payment processing

### 👨‍💼 Admin Features

#### Product Management
- ➕ Create, update, and delete products
- 📁 Category management system
- 🖼️ Multiple product image upload
- 📊 Stock management and tracking
- 🎯 Offer and discount management
- 🔍 Product search and filtering

#### Order Management
- 📋 View and manage all orders
- ✅ Update order status
- 👥 User management
- 📈 Sales analytics

#### Content Management
- 🎨 Customizable categories
- 📝 Product descriptions and details
- 🏷️ Pricing and inventory control

## 🛠️ Tech Stack

### Backend Technologies
- **Framework**: Django 5.1.2
- **Language**: Python 3.12+
- **Database**: PostgreSQL 12+
- **Server**: Gunicorn
- **Static Files**: WhiteNoise

### Frontend Technologies
- **Markup**: HTML5
- **Styling**: CSS3, Bootstrap
- **Scripting**: JavaScript
- **Responsive**: Mobile-first design

### Key Libraries & Tools
| Library | Purpose |
|---------|---------|
| `django-allauth` | Authentication system |
| `social-auth-app-django` | Social authentication |
| `psycopg2` | PostgreSQL adapter |
| `Pillow` | Image processing |
| `razorpay` | Payment gateway |
| `weasyprint` | PDF generation |
| `python-decouple` | Environment management |
| `whitenoise` | Static file serving |

## 🏁 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python** 3.12 or higher
- **PostgreSQL** 12 or higher
- **pip** (Python package manager)
- **Git** (for version control)
- **Virtual Environment** (recommended)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/Niaal-B/Django_Ecommerce.git
cd Django_Ecommerce

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables (see Configuration section)
cp .env.example .env  # Edit .env with your settings

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to see the application.

## 📦 Installation

### Step-by-Step Guide

#### 1. Clone the Repository

```bash
git clone https://github.com/Niaal-B/Django_Ecommerce.git
cd Django_Ecommerce
```

#### 2. Create Virtual Environment

```bash
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Database Setup

```bash
# Login to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE evara;

# Create user (optional)
CREATE USER evara_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE evara TO evara_user;

# Exit PostgreSQL
\q
```

#### 5. Environment Configuration

Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here-generate-with-command-below
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_NAME=evara
DB_USER=evara_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Email Configuration (Gmail)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password

# Social Authentication (Google OAuth)
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=your-google-client-id
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=your-google-client-secret
```

**Generate Django Secret Key:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### 6. Run Migrations

```bash
python manage.py migrate
```

#### 7. Create Superuser

```bash
python manage.py createsuperuser
```

#### 8. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

#### 9. Run Development Server

```bash
python manage.py runserver
```

Your application will be available at `http://127.0.0.1:8000`

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SECRET_KEY` | Django secret key | ✅ Yes | - |
| `DEBUG` | Debug mode | ✅ Yes | `False` |
| `ALLOWED_HOSTS` | Allowed hosts (comma-separated) | ✅ Yes | - |
| `DB_NAME` | Database name | ✅ Yes | `evara` |
| `DB_USER` | Database user | ✅ Yes | - |
| `DB_PASSWORD` | Database password | ✅ Yes | - |
| `DB_HOST` | Database host | ✅ Yes | `localhost` |
| `DB_PORT` | Database port | ✅ Yes | `5432` |
| `EMAIL_HOST_USER` | Email address | ⚠️ Optional | - |
| `EMAIL_HOST_PASSWORD` | Email app password | ⚠️ Optional | - |
| `SOCIAL_AUTH_GOOGLE_OAUTH2_KEY` | Google OAuth Client ID | ⚠️ Optional | - |
| `SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET` | Google OAuth Secret | ⚠️ Optional | - |

### Email Configuration

To enable email functionality (OTP verification, password reset):

1. **For Gmail:**
   - Enable 2-Factor Authentication
   - Go to Google Account → Security → App Passwords
   - Generate an App Password for "Mail"
   - Use the generated password in `EMAIL_HOST_PASSWORD`

2. **For Other Providers:**
   - Update `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS` in `settings.py`
   - Configure credentials accordingly

### Google OAuth Setup

1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs:
   - Development: `http://localhost:8000/social-auth/complete/google-oauth2/`
   - Production: `https://yourdomain.com/social-auth/complete/google-oauth2/`
6. Copy Client ID and Secret to `.env` file


[⬆ Back to Top](#-evara---django-e-commerce-platform)

</div>
