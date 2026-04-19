from django.urls import path
from . import views

urlpatterns = [
    path("",views.account,name='account'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('add_address/', views.add_address, name='add_address'),
    path('edit-address/', views.edit_address, name='edit_address'),
    path('delete-address/<int:address_id>/', views.delete_address, name='delete_address'),
    path('update_password/',views.update_password,name='update_password'),
    path('order/<int:order_id>/details/', views.view_order_items, name='view_order_items'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('cancel-order-item/<int:item_id>/', views.cancel_order_item, name='cancel_order_item'),
    path('return-order/<int:order_id>/', views.return_order, name='return_order'),
    ]