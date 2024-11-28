from django.urls import path
from . import views

urlpatterns = [
   path('login/', views.admin_login, name='admin_login'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('users/',views.user_manage,name='users'),
    path('users/block/<int:user_id>/', views.block_user, name='block_user'),
    path('users/unblock/<int:user_id>/', views.unblock_user, name='unblock_user'),
    path('logout/', views.admin_logout, name='logout'),
    path('active-users/', views.active_users_count, name='active_user_count'),
    path('delivered-revenue/', views.delivered_revenue, name='delivered_revenue'),
    path('total-orders',views.total_orders,name='total_orders'),
    path('orders-in-progress/', views.orders_in_progress, name='orders_in_progress'),
    path('top-selling-products/', views.top_selling_products, name='top_selling_products'),
    path('category_wise_sales/', views.category_wise_sales, name='category_wise_sales'),
    path('sales-statistics/', views.sales_statistics, name='sales_statistics'),
    path('generate-sales-report/', views.generate_sales_report_pdf, name='generate_sales_report'),
    path('coupon-discount/',views.coupon_discount,name='coupon_discount'),
    path('offer-discount/',views.offer_discount,name='offer_discount')
    ]