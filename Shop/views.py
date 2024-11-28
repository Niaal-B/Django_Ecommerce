from django.shortcuts import render
from Products.models import Product
from Categories.models import Category
from django.core.paginator import Paginator

# Create your views here.
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
        

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    

    products_count = products.count()
    

    paginator = Paginator(products,6) 
    

    page_number = request.GET.get('page', 1)
    

    page_obj = paginator.get_page(page_number)
    

    context = {
        'products': page_obj, 
        'products_count': products_count,  
    }
    

    return render(request, 'shop.html', context)
