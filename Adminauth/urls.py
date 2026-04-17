from django.urls import path
from . import views

urlpatterns = [
   path('login/', views.admin_login, name='admin_login'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('users/',views.user_manage,name='users'),
    path('users/block/<int:user_id>/', views.block_user, name='block_user'),
    path('users/unblock/<int:user_id>/', views.unblock_user, name='unblock_user'),
    path('logout/', views.admin_logout, name='logout'),
    path('panel/year/<int:year>/', views.chart_year_data, name='chart_year_data'),
    path('coupon/', views.coupon_management, name='coupon_management'),
    path('coupon/add/', views.add_coupon, name='add_coupon'),
    path('coupon/edit/<int:coupon_id>/', views.edit_coupon, name='edit_coupon'),
    path('coupon/delete/<int:coupon_id>/', views.delete_coupon, name='delete_coupon'),
]