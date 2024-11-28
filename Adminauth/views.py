from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test,login_required
from django.contrib import messages
from django.http import JsonResponse
from Order.models import Order,OrderItem
from django.db.models import Sum
from Categories.models import Category
from Products.models import Product
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.cache import never_cache
from django.db.models.functions import TruncDay
from django.utils.timezone import datetime
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML
from decimal import Decimal
from datetime import datetime
from django.utils.timezone import make_aware


def is_admin(user):
    return user.is_staff

@never_cache
def admin_login(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard')

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
    recent_orders = Order.objects.order_by('-created_at')[:10]
    context = {
        'recent_orders' : recent_orders
    }
    return render(request, 'admin/dashboard.html',context)

@user_passes_test(is_admin)
def user_manage(request):
    users = User.objects.filter(is_superuser=False).order_by('-date_joined')

    return render(request,'admin/users.html',{'users':users})

@user_passes_test(is_admin)
def block_user(request,user_id):
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

def get_date_range(filter_type):
    today = timezone.now().date()
    
    if filter_type == 'today':
        return today, today
    elif filter_type == 'week':
        start_date = today - timedelta(days=today.weekday())
        return start_date, today
    elif filter_type == 'month':
        start_date = today.replace(day=1)
        return start_date, today
    return None, None



def active_users_count(request):
    filter_type = request.GET.get('filter')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    query = User.objects.filter(is_active=True)
    
    if filter_type:
        start, end = get_date_range(filter_type)
        if start and end:
            query = query.filter(date_joined__date__range=[start, end])
    elif start_date and end_date:
        query = query.filter(date_joined__date__range=[start_date, end_date])
    
    active_users = query.count()
    return JsonResponse({'active_users': active_users})



def delivered_revenue(request):
    filter_type = request.GET.get('filter')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    query = Order.objects.filter(status="Delivered")
    
    if filter_type:
        start, end = get_date_range(filter_type)
        if start and end:
            query = query.filter(created_at__date__range=[start, end])
    elif start_date and end_date:
        query = query.filter(created_at__date__range=[start_date, end_date])
    
    total_revenue = query.aggregate(total=Sum('total_price'))['total'] or 0
    return JsonResponse({'total_revenue': total_revenue})



def total_orders(request):
    filter_type = request.GET.get('filter')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    query = Order.objects
    
    if filter_type:
        start, end = get_date_range(filter_type)
        if start and end:
            query = query.filter(created_at__date__range=[start, end])
    elif start_date and end_date:
        query = query.filter(created_at__date__range=[start_date, end_date])
    
    total_orders = query.count()
    return JsonResponse({'total_orders': total_orders})




def orders_in_progress(request):
    filter_type = request.GET.get('filter')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    
    query = Order.objects.filter(status__in=["pending", "shipped"])
    
    
    if filter_type:
        start, end = get_date_range(filter_type)
        if start and end:
            query = query.filter(created_at__date__range=[start, end])
            
    elif start_date and end_date:
        query = query.filter(created_at__date__range=[start_date, end_date])
    
    in_progress = query.count()
    return JsonResponse({'orders_in_progress': in_progress})


def coupon_discount(request):
    filter_type = request.GET.get('filter')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    query = Order.objects.all()  
    

    if filter_type:
    
        start, end = get_date_range(filter_type)

 
        if start and end:
            query = query.filter(created_at__date__range=[start, end])
            print(query,"this is coupon query")
    elif start_date and end_date:
        query = query.filter(created_at__date__range=[start_date, end_date])
    
    # Aggregate the total coupon discount
    total_coupon_discount = query.aggregate(total_discount=Sum('discount'))['total_discount'] or Decimal('0.00')
    print(total_coupon_discount,"this is total coupon discount")
    
    return JsonResponse({'total_coupon_discount': total_coupon_discount})


from django.db.models import Sum
from decimal import Decimal
from django.http import JsonResponse

def offer_discount(request):
    # Get filter parameters
    filter_type = request.GET.get('filter')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Base query for order items
    query = OrderItem.objects.all()
    
    if filter_type:
        # Get date range based on the filter type
        start, end = get_date_range(filter_type)
        
        if start and end:
            # Filter by the calculated date range
            query = query.filter(order__created_at__date__range=[start, end])
    elif start_date and end_date:
        # Filter by custom date range
        query = query.filter(order__created_at__date__range=[start_date, end_date])
    
    # Aggregate the total offer discount
    total_order_item_discount = query.aggregate(
        total_order_item_discount=Sum('discount')
    )['total_order_item_discount'] or Decimal('0.00')
    
    return JsonResponse({'order_item_discount': total_order_item_discount})


def top_selling_products(request):
    filter_type = request.GET.get('filter')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    query = OrderItem.objects
    
    if filter_type:
        start, end = get_date_range(filter_type)
        if start and end:
            query = query.filter(order__created_at__date__range=[start, end])
    elif start_date and end_date:
        query = query.filter(order__created_at__date__range=[start_date, end_date])
    
    top_products = (
        query.values('product__name')
        .annotate(total_quantity=Sum('quantity'))
        .order_by('-total_quantity')[:5]
    )
    
    product_names = [item['product__name'] for item in top_products]
    quantities = [item['total_quantity'] for item in top_products]
    
    return JsonResponse({'product_names': product_names, 'quantities': quantities})


def category_wise_sales(request):
    filter_type = request.GET.get('filter')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    query = OrderItem.objects
    
    if filter_type:
        start, end = get_date_range(filter_type)
        if start and end:
            query = query.filter(order__created_at__date__range=[start, end])
    elif start_date and end_date:
        query = query.filter(order__created_at__date__range=[start_date, end_date])
    
    category_sales = (
        query.values('product__category__category_name')
        .annotate(sales=Sum('quantity'))
        .exclude(product__category__category_name=None)
    )
    
    labels = [entry['product__category__category_name'] for entry in category_sales]
    sales_data = [entry['sales'] for entry in category_sales]
    
    return JsonResponse({
        'labels': labels,
        'sales_data': sales_data
    })



def sales_statistics(request):
    filter_type = request.GET.get('filter')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if filter_type:
        start, end = get_date_range(filter_type)
    elif start_date and end_date:
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        end = timezone.now().date()
        start = end - timedelta(days=7)
    
    daily_sales = Order.objects.filter(
        created_at__date__range=[start, end],
        status='Delivered',
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        total_sales=Sum('total_price')
    ).order_by('date')
    
    dates = []
    sales_data = []
    
    for entry in daily_sales:
        dates.append(entry['date'].strftime('%Y-%m-%d'))
        sales_data.append(float(entry['total_sales']))
    
    return JsonResponse({
        'dates': dates,
        'sales_data': sales_data
    })



def generate_sales_report_pdf(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:

        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)


        start_date = make_aware(start_date)
        end_date = make_aware(end_date)


        query = OrderItem.objects.all()
        query = query.filter(order__created_at__range=(start_date, end_date))

        total_order_item_discount = query.aggregate(
            total_order_item_discount=Sum('discount')
        )['total_order_item_discount'] or Decimal('0.00')

        total_revenue = query.aggregate(total=Sum('price'))['total'] or Decimal('0.00')


        orders = Order.objects.filter(created_at__range=(start_date, end_date))
        print(orders)


        html_content = render_to_string('admin/sales_report.html', {
            'orders': orders,
            'start_date': start_date,
            'end_date': end_date,
            'total_revenue': total_revenue,
            'total_order_item_discount': total_order_item_discount,
        })


        pdf_file = HTML(string=html_content).write_pdf()


        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="sales_report_{start_date.date()}_{end_date.date()}.pdf"'
        return response

  
    return HttpResponse("Invalid date range", status=400)


