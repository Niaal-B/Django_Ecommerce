# urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("login/", views.user_login, name='userlogin'),
    path("register/", views.register, name='register'),
    path('otp/<str:email>/', views.verify_otp, name='verify_otp'),
    path('logout/',views.user_logout,name='userlogout'),
    path('otp/resend/<str:email>/',views.resend_otp, name='resend_otp'),
     path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-forgot-password/<str:email>/', views.verify_forgot_password, name='verify_forgot_password'),
    path('reset-password/<email>/', views.reset_password, name='reset_password'),

]
