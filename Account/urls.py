from django.urls import path
from . import views

urlpatterns = [
    path("",views.account,name='account'),
    path('update-username/', views.update_username, name='update_username'),
    path('add_address/', views.add_address, name='add_address'),
    path('edit-address/', views.edit_address, name='edit_address'),
    path('delete-address/<int:address_id>/', views.delete_address, name='delete_address'),
    path('update_password/',views.update_password,name='update_password'),
    path('order/<int:order_id>/details/', views.view_order_items, name='view_order_items'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('request-return/', views.request_return, name='request_return'),
    path('cancel-item-order/',views.cancel_item_order,name='cancel_item_order'),
    path('add-money-to-wallet/', views.add_money_to_wallet, name='add_money_to_wallet'),
    ]