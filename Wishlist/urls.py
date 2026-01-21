from django.urls import path
from . import views

urlpatterns = [
    path("", views.wishlist, name='wishlist'),
    path('add/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove/', views.remove_from_wishlist, name='remove_from_wishlist'),
]

