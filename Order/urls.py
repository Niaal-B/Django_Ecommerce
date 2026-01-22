from django.urls import path
from . import views

urlpatterns = [
    path("order/",views.place_order,name='place_order'),
    path("order/success/",views.order_success,name='order_success'),
    path("payment_success/", views.payment_success, name='payment_success'),
    path("order-management/",views.order_management,name='order_management'),
    path('order-view/<int:order_id>/', views.admin_order_details, name='order-view'),
]