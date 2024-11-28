from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import json
from . models import Wishlist
from Products.models import Product,SizeVariant

# Create your views here.
@login_required
def wishlist(request):
    
    wishlist_items = Wishlist.objects.filter(user=request.user)
    
  
    items_with_stock = []
    
    for item in wishlist_items:
        item_check = SizeVariant.objects.get(size=item.size, product=item.product)
        stock = item_check.stock
        

        stock_status = "Available" if stock > 0 else "Out of Stock"
        

        items_with_stock.append({
            "item": item,
            "stock_status": stock_status
        })
    
    context = {
        "wishlist_items": items_with_stock
    }
    return render(request, 'wishlist.html', context)



@require_POST
@login_required
def toggle_wishlist(request):
        data = json.loads(request.body)
        print(data)
        product_id = data.get('product_id')
        size = data.get('size')
    

        product = Product.objects.get(id=product_id)
        wishlist_item = Wishlist.objects.filter(
            user=request.user,
            product=product,
            size=size
        ).first()
        
        if wishlist_item:
            wishlist_item.delete()
            return JsonResponse({
                'success': True,
                'added': False,
                'message': 'Removed from wishlist'
            })
        else:
       
            Wishlist.objects.create(
                user=request.user,
                product=product,
                size=size
            )
            return JsonResponse({
                'success': True,
                'added': True,
                'message': 'Added to wishlist'
            })
            

def remove_from_wishlist(request,item_id):
    item = Wishlist.objects.get(id=item_id)
    item.delete()
    return redirect('wishlist')

    
            