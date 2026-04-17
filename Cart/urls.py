from django.urls import path
from . import views

urlpatterns = [
    path("",views.cart,name='cart'),
     path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
     path('remove-item/', views.remove_item_from_cart, name='remove_item_from_cart'),  
     path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
     path('remove-coupon/', views.remove_coupon, name='remove_coupon'),
    ]