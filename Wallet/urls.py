from django.urls import path
from . import views

urlpatterns = [
    path('history/', views.wallet_history, name='wallet_history'),
]
