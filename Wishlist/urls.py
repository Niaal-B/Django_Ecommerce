from django.urls import path
from . import views

urlpatterns = [
    path("",views.wishlist,name='wishlist'),
    path('toggle-wishlist/', views.toggle_wishlist, name='toggle_wishlist'),
    path('remove_item/<int:item_id>',views.remove_from_wishlist,name='remove_wishlist_item')
]