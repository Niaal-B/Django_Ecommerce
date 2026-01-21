from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json
from .models import Wishlist, WishlistItem
from Products.models import Product


@login_required
def wishlist(request):
    wishlist_obj, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist_items = wishlist_obj.items.all()
    items_count = wishlist_items.count()
    
    context = {
        'items': wishlist_items,
        'items_count': items_count,
    }
    return render(request, 'wishlist.html', context)


def add_to_wishlist(request):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            
            if not product_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Product ID is required'
                }, status=400)
            
            product = get_object_or_404(Product, id=product_id)
            wishlist_obj, created = Wishlist.objects.get_or_create(user=request.user)
            
            # Check if product already in wishlist
            existing_item = WishlistItem.objects.filter(
                wishlist=wishlist_obj, 
                product=product
            ).first()
            
            if existing_item:
                return JsonResponse({
                    'success': False,
                    'message': 'Product is already in your wishlist'
                })
            
            wishlist_item = WishlistItem(wishlist=wishlist_obj, product=product)
            wishlist_item.save()
            
            return JsonResponse({
                'success': True, 
                'message': 'Product added to wishlist'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'success': False, 
        'message': 'User not authenticated or invalid request'
    }, status=400)


@login_required
def remove_from_wishlist(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            
            if not product_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Product ID is required'
                }, status=400)
            
            wishlist_obj = get_object_or_404(Wishlist, user=request.user)
            wishlist_item = get_object_or_404(
                WishlistItem, 
                wishlist=wishlist_obj, 
                product_id=product_id
            )
            wishlist_item.delete()
            
            return JsonResponse({
                'success': True, 
                'message': 'Product removed from wishlist'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'success': False, 
        'message': 'Invalid request'
    }, status=400)

