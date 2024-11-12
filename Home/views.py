from django.shortcuts import render
from Categories.models import Category
from Products.models import Product
from django.utils import timezone
from datetime import timedelta

# Create your views here.
def index(request):
    categories = Category.objects.filter(is_listed=True)
    last_week = timezone.now() - timedelta(days=7)
    recent_products = Product.objects.filter(created_at__gte=last_week,category__is_listed=True)
    deals_products = Product.objects.filter(offer__gte=1,category__is_listed=True)

    context = {
        'categories' : categories,
        'recent_products' : recent_products,
        'deals_products' : deals_products
    }
    return render(request,'index.html',context)