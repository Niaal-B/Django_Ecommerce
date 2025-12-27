# 🛒 Evara - Django E-commerce Platform

<div align="center">

[![Django](https://img.shields.io/badge/Django-5.1.2-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**A modern, full-featured e-commerce web application built with Django**

[Features](#-features) • [Installation](#-installation) • [Deployment](#️-deployment-on-render) • [Documentation](#-documentation)

</div>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#️-tech-stack)
- [Getting Started](#-getting-started)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Deployment](#️-deployment)
- [Project Structure](#-project-structure)
- [API Documentation](#-api-documentation)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

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

## 🐳 Docker Deployment

### Using Docker Compose

The easiest way to deploy using Docker:

```bash
# Build and start containers
docker-compose up --build

# Run in detached mode
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop containers
docker-compose down

# Stop and remove volumes (clears database)
docker-compose down -v
```

### Docker Services

- **web**: Django application (port 8000)
- **db**: PostgreSQL database (port 5432)

### Default Docker Credentials

- Database: `evara`
- User: `evara_user`
- Password: `evara_password`

## ☁️ Deployment on Render

### Prerequisites
- GitHub repository
- Render account ([Sign up here](https://render.com))

### Deployment Steps

#### Option 1: Using render.yaml (Recommended)

1. **Push code to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push origin master
   ```

2. **Deploy via Render Dashboard**
   - Go to Render Dashboard → New → Blueprint
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml`
   - Review and apply the configuration

#### Option 2: Manual Setup

1. **Create PostgreSQL Database**
   - Go to Render Dashboard → New → PostgreSQL
   - Name: `evara-postgres`
   - Plan: Free (or choose based on needs)
   - Note the connection details

2. **Create Web Service**
   - Go to Render Dashboard → New → Web Service
   - Connect your GitHub repository
   - Configure:
     - **Name**: `evara-django-app`
     - **Environment**: Python 3
     - **Build Command**: 
       ```bash
       pip install --upgrade pip && pip install -r requirements.txt && python manage.py migrate --noinput && python manage.py collectstatic --noinput
       ```
     - **Start Command**:
       ```bash
       gunicorn Evara.wsgi:application --bind 0.0.0.0:$PORT --timeout 120
       ```

3. **Set Environment Variables**
   Add all required environment variables in the Environment tab

4. **Link Database** (Manual setup only)
   - In web service → Environment tab
   - Click "Link PostgreSQL Database"
   - Select your database

### Post-Deployment

1. Update `ALLOWED_HOSTS` with your Render domain
2. Verify all environment variables are set
3. Check logs for any errors
4. Test the application

## 📁 Project Structure

```
Django_Ecommerce/
│
├── Account/              # User account management
│   ├── models.py        # User profile and address models
│   ├── views.py         # Account-related views
│   └── urls.py          # Account URL patterns
│
├── Adminauth/           # Admin authentication
│   └── views.py         # Admin login/logout
│
├── Cart/                # Shopping cart functionality
│   ├── models.py        # Cart and CartItem models
│   ├── views.py         # Cart operations
│   └── context_processors.py  # Cart item count
│
├── Categories/          # Product categories
│   ├── models.py        # Category model
│   └── admin.py         # Category admin interface
│
├── Evara/               # Main project directory
│   ├── settings.py      # Django settings
│   ├── urls.py          # Main URL configuration
│   └── wsgi.py          # WSGI configuration
│
├── Home/                # Homepage
│   └── views.py         # Homepage view
│
├── Order/               # Order processing
│   ├── models.py        # Order and OrderItem models
│   └── views.py         # Checkout and order views
│
├── Products/            # Product management
│   ├── models.py        # Product and SizeVariant models
│   └── views.py         # Product views
│
├── Shop/                # Shop/listing views
│   └── views.py         # Product listing and filtering
│
├── UserAuth/            # User authentication
│   ├── models.py        # OTP model
│   ├── views.py         # Registration, login, OTP
│   └── urls.py          # Auth URL patterns
│
├── assets/              # Collected static files (production)
├── media/               # User uploaded files
├── static/              # Static files (CSS, JS, images)
├── templates/           # HTML templates
│
├── .env                 # Environment variables (gitignored)
├── .gitignore           # Git ignore rules
├── requirements.txt     # Python dependencies
├── render.yaml          # Render deployment config
├── docker-compose.yml   # Docker Compose config
├── Dockerfile           # Docker image config
├── build.sh             # Build script
└── manage.py            # Django management script
```
## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. **Make your changes**
4. **Commit your changes**
   ```bash
   git commit -m 'Add some AmazingFeature'
   ```
5. **Push to the branch**
   ```bash
   git push origin feature/AmazingFeature
   ```
6. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guide
- Write meaningful commit messages
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Nihal B**

- GitHub: [@Niaal-B](https://github.com/Niaal-B)
- Project Link: [https://github.com/Niaal-B/Django_Ecommerce](https://github.com/Niaal-B/Django_Ecommerce)

## 🙏 Acknowledgments

- [Django](https://www.djangoproject.com/) - The web framework for perfectionists
- [PostgreSQL](https://www.postgresql.org/) - The world's most advanced open source database
- All open-source libraries and contributors
- Django community for excellent documentation and support

## 📞 Support

Need help? Here are some resources:

- 📖 Check the [Documentation](#-documentation)
- 🐛 [Open an Issue](https://github.com/Niaal-B/Django_Ecommerce/issues)
- 💬 Start a [Discussion](https://github.com/Niaal-B/Django_Ecommerce/discussions)
- 📧 Email: [your-email@gmail.com](mailto:your-email@gmail.com)

## ⭐ Show Your Support

If you find this project helpful, please give it a ⭐ on GitHub!

---

<div align="center">

**Made with ❤️ using Django**

[⬆ Back to Top](#-evara---django-e-commerce-platform)

</div>

---

**⚠️ Important Notes:**

- Never commit `.env` file or sensitive information to version control
- Always use environment variables for configuration in production
- Keep your `SECRET_KEY` secure and never share it publicly
- Regularly update dependencies for security patches
- Test thoroughly before deploying to production
