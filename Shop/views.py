from django.shortcuts import render
from Products.models import Product
from Categories.models import Category
from django.core.paginator import Paginator
from django.conf import settings
import logging
from decimal import Decimal, InvalidOperation

logger = logging.getLogger(__name__)

def shop(request):
    
    category_id = request.GET.get('category_id')
    if category_id:
        products = Product.objects.filter(
            category_id=category_id, 
            is_listed=True, 
            category__is_listed=True
        )
    else:
        products = Product.objects.filter(
            is_listed=True, 
            category__is_listed=True
        )
    sort = request.GET.get('sort')
    if sort == 'name_asc':
        products = products.order_by('name')
    elif sort == 'name_desc':
        products = products.order_by('-name')
    elif sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    else:
        products = products.order_by('-created_at')


    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    try:
        if min_price:
            products = products.filter(price__gte=Decimal(min_price))
        if max_price:
            products = products.filter(price__lte=Decimal(max_price))
    except (ValueError, InvalidOperation):
        logger.warning(f"Invalid price filter values received: min={min_price}, max={max_price}")
        # Continue with unfiltered products or previous filters
    

    products_count = products.count()
    
    paginator = Paginator(products, settings.ITEMS_PER_PAGE) 
    

    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.get_page(page_number)
    except Exception as e:
        logger.error(f"Pagination error: {str(e)}", exc_info=True)
        page_obj = paginator.get_page(1)
    

    context = {
        'products': page_obj, 
        'products_count': products_count,  
    }
    

    return render(request, 'shop.html', context)
