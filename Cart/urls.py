from django.urls import path
from . import views

urlpatterns = [
    path("",views.cart,name='cart'),
     path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
     path('remove-item/', views.remove_item_from_cart, name='remove_item_from_cart'),  
    ]