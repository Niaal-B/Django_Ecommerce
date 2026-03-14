from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test, login_required
from django.db.models import Sum, Count, F
from django.db.models.functions import ExtractMonth
from django.http import JsonResponse
from Order.models import Order, OrderItem
from Products.models import Product, SizeVariant
from Categories.models import Category
from Account.models import Address

def is_admin(user):
    return user.is_staff

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid credentials or not an admin user.')

    return render(request, 'admin/admin_login.html')

@user_passes_test(is_admin)
@login_required(login_url='admin_login')
def admin_dashboard(request):
    # Total Sales and Count
    total_sales = Order.objects.aggregate(total=Sum('total_price'))['total'] or 0
    sales_count = Order.objects.count()

    # Top-Selling Categories
    top_category = OrderItem.objects.values(
        'product__category__category_name'
    ).annotate(
        total_quantity_sold=Sum('quantity'),
        total_revenue=Sum(F('quantity') * F('price'))
    ).order_by('-total_quantity_sold')[:5]

    # Top-Selling Products
    top_products = OrderItem.objects.values(
        'product__id',
        'product__name',
        'product__image1'
    ).annotate(
        product__product_name=F('product__name'),
        product__image_1=F('product__image1'),
        total_quantity_sold=Sum('quantity'),
        total_revenue=Sum(F('quantity') * F('price')),
        product__available_stock=Sum('product__size_variants__stock')
    ).order_by('-total_quantity_sold')[:5]

    # Top Customers
    top_customers = Order.objects.values(
        'user__username'
    ).annotate(
        username=F('user__username'),
        total_orders=Count('id'),
        total_spend=Sum('total_price')
    ).order_by('-total_spend')[:5]

    # Orders by Pincode
    orders_by_pincode = Order.objects.values(
        'address__postcode',
        'address__state',
        'address__city'
    ).annotate(
        user__addresses__pincode=F('address__postcode'),
        user__addresses__state=F('address__state'),
        user__addresses__district=F('address__city'),
        total_orders=Count('id')
    ).order_by('-total_orders')[:10]

    # Data for Pie Chart
    categories = [cat['product__category__category_name'] for cat in top_category]
    quantities = [cat['total_quantity_sold'] for cat in top_category]

    context = {
        'total_sales': total_sales,
        'sales_count': sales_count,
        'top_category': top_category,
        'top_products': top_products,
        'top_customers': top_customers,
        'orders_by_pincode': orders_by_pincode,
        'categories': categories,
        'quantities': quantities,
    }
    return render(request, 'admin/dashboard.html', context)

@user_passes_test(is_admin)
@login_required(login_url='admin_login')
def chart_year_data(request, year):
    # Monthly sales for the specific year
    monthly_data = Order.objects.filter(
        created_at__year=year
    ).annotate(
        month=ExtractMonth('created_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')

    # Mapping month numbers to names (optional, JS handles labels usually)
    month_labels = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]
    
    # Initialize data list with 0s
    data_points = [0] * 12
    for entry in monthly_data:
        data_points[entry['month'] - 1] = entry['count']

    return JsonResponse({
        'labels': month_labels,
        'data': data_points
    })

@user_passes_test(is_admin)
def user_manage(request):
    users = User.objects.filter(is_superuser=False).order_by('-date_joined')
    return render(request, 'admin/users.html', {'users': users})

@user_passes_test(is_admin)
def block_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = False
    user.save()
    messages.success(request, f'{user.username} has been blocked.')
    return redirect('users')

@user_passes_test(is_admin)
def unblock_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = True
    user.save()
    messages.success(request, f'{user.username} has been unblocked.')
    return redirect('users')

@login_required(login_url='admin_login')
def admin_logout(request):
    logout(request)
    return redirect('admin_login')