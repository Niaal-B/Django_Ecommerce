from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .models import OTP
import random
from Home import views
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import re

def generate_otp():
    return random.randint(100000, 999999)

def send_otp_email(email, otp):
    subject = 'Your OTP Code'
    message = f'Your OTP code is: {otp}'
    try:
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "")
        api_key = getattr(settings, "SENDGRID_API_KEY", "")

        if not from_email:
            print("Warning: DEFAULT_FROM_EMAIL not configured. OTP email cannot be sent.")
            return False

        if not api_key:
            print("Warning: SENDGRID_API_KEY not configured. OTP email cannot be sent.")
            return False

        try:
            sg = SendGridAPIClient(api_key)
            mail = Mail(
                from_email=from_email,
                to_emails=email,
                subject=subject,
                plain_text_content=message,
            )
            response = sg.send(mail)
            if 200 <= response.status_code < 300:
                print(f"OTP email sent successfully to {email}")
                return True
            else:
                print(f"Failed to send email to {email}: status {response.status_code}")
                print(f"Response body: {response.body}")
                print(f"Response headers: {response.headers}")
                return False
        except Exception as email_error:
            print(f"Email sending error: {type(email_error).__name__}: {str(email_error)}")
            # Log more details if it's a SendGrid exception
            if hasattr(email_error, 'body'):
                print(f"SendGrid error body: {email_error.body}")
            if hasattr(email_error, 'status_code'):
                print(f"SendGrid status code: {email_error.status_code}")
            return False
    except Exception as e:
        print(f"Error in send_otp_email: {type(e).__name__}: {str(e)}")
        return False

def validate_password(password):
    """
    Validate password strength
    Returns (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character."
    return True, ""

def validate_username(username):
    """
    Validate username format
    Returns (is_valid, error_message)
    """
    if len(username) < 3:
        return False, "Username must be at least 3 characters long."
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return False, "Username can only contain letters, numbers, and underscores."
    return True, ""

def validate_name(name):
    """
    Validate first/last name format
    Returns (is_valid, error_message)
    """
    if not name or len(name) < 2:
        return False, "Name must be at least 2 characters long."
    if not re.match(r"^[a-zA-Z\s-]+$", name):
        return False, "Name can only contain letters, spaces, and hyphens."
    return True, ""

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validate all fields
        errors = {}

        # Username validation
        username_valid, username_error = validate_username(username)
        if not username_valid:
            errors['username'] = username_error
        elif User.objects.filter(username=username).exists():
            errors['username'] = "Username already taken."

        # Name validation
        first_name_valid, first_name_error = validate_name(first_name)
        if not first_name_valid:
            errors['first_name'] = first_name_error

        last_name_valid, last_name_error = validate_name(last_name)
        if not last_name_valid:
            errors['last_name'] = last_name_error

        # Email validation
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            errors['email'] = "Please enter a valid email address."
        elif User.objects.filter(email=email).exists():
            errors['email'] = "Email already registered."

        # Password validation
        password_valid, password_error = validate_password(password)
        if not password_valid:
            errors['password'] = password_error
        elif password != confirm_password:
            errors['confirm_password'] = "Passwords do not match."

        if errors:
            return render(request, 'register.html', {
                'errors': errors,
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'email': email
            })

        # If validation passes, proceed with registration
        try:
            otp = generate_otp()
            expires_at = timezone.now() + timedelta(minutes=5)
            
            # Create or update OTP
            OTP.objects.update_or_create(
                email=email,
                defaults={'otp': otp, 'expires_at': expires_at}
            )

            # Send OTP email
            email_sent = send_otp_email(email, otp)
            if not email_sent:
                # Check if email is configured
                if not getattr(settings, 'EMAIL_HOST_USER', ''):
                    errors['email'] = "Email service is not configured. Please contact administrator."
                else:
                    errors['email'] = "Failed to send OTP email. Please check your email address and try again."
                return render(request, 'register.html', {
                    'errors': errors,
                    'username': username,
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email
                })

            # Store user information in session
            request.session['registration_data'] = {
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'password': password
            }

            return redirect('verify_otp', email=email)

        except Exception as e:
            errors['general'] = "An error occurred. Please try again."
            return render(request, 'register.html', {
                'errors': errors,
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'email': email
            })

    return render(request, 'register.html')

def verify_otp(request, email):
    if not request.session.get('registration_data'):
        return redirect('register')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')

        try:
            otp_instance = OTP.objects.get(email=email)
            
            if otp_instance.is_expired():
                return render(request, 'verify_otp.html', {
                    'email': email,
                    'error': 'OTP has expired. Please request a new one.'
                })

            if str(otp_instance.otp) == entered_otp:
                # Get registration data from session
                registration_data = request.session['registration_data']
                
                # Create user
                user = User.objects.create_user(
                    username=registration_data['username'],
                    email=registration_data['email'],
                    password=registration_data['password'],
                    first_name=registration_data['first_name'],
                    last_name=registration_data['last_name']
                )

                # Clean up
                del request.session['registration_data']
                otp_instance.delete()

                # Log the user in
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
                
                return redirect('home')
            else:
                return render(request, 'otp.html', {
                    'email': email,
                    'error': 'Invalid OTP. Please try again.'
                })

        except OTP.DoesNotExist:
            return render(request, 'otp.html', {
                'email': email,
                'error': 'OTP not found. Please register again.'
            })

    return render(request, 'otp.html', {'email': email})

def resend_otp(request, email):
    if request.method == 'POST':
        try:
            # Check if OTP exists and handle cooldown
            try:
                otp_instance = OTP.objects.get(email=email)
                time_elapsed = timezone.now() - otp_instance.updated_at
                
                if time_elapsed < timedelta(seconds=30):
                    seconds_remaining = 30 - time_elapsed.seconds
                    return JsonResponse({
                        'success': False,
                        'message': f'Please wait {seconds_remaining} seconds before requesting a new OTP.'
                    })
            except OTP.DoesNotExist:
                pass

            # Generate and save new OTP
            otp = generate_otp()
            expires_at = timezone.now() + timedelta(minutes=5)
            
            OTP.objects.update_or_create(
                email=email,
                defaults={'otp': otp, 'expires_at': expires_at}
            )

            # Send OTP
            if send_otp_email(email, otp):
                return JsonResponse({
                    'success': True,
                    'message': 'New OTP sent successfully!'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Failed to send OTP. Please try again.'
                })

        except Exception as e:
            print(f"Error in resend_otp: {e}")
            return JsonResponse({
                'success': False,
                'message': 'An error occurred. Please try again.'
            })

    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.'
    })

def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            return render(request, 'login.html', {
                'error': 'Please enter both username and password.'
            })

        # Check if the user exists
        try:
            user = User.objects.get(username=username)
            if not user.is_active:
                messages.error(request, "You are blocked.")
                return render(request, 'login.html')
        except User.DoesNotExist:
            user = None

        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to home after successful login
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    return redirect('home')