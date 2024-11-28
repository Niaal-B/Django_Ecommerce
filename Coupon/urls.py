from django.urls import path
from . import views


urlpatterns = [
    path("management/",views.coupon_management,name='coupon_management'),
    path("create/",views.create_coupon,name='create_coupon'),
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('delete/<int:coupon_id>',views.delete_coupon,name='delete_coupon')
]