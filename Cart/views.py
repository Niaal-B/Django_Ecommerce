from django.shortcuts import render,redirect,get_object_or_404
from django.http import JsonResponse
import json
from .models import Cart,CartItem
from Products.models import Product


# Create your views here.
def cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        user_cart = cart.items.all()
        items_count = user_cart.count()
        if request.method == 'POST':
            for item in CartItem.objects.filter(cart=request.user.cart):
                quantity = request.POST.get(f'quantity_{item.id}')

                if quantity:
                    item.quantity = int(float(quantity))  
                    item.save()
        for item in user_cart:
            item.stock = item.product.size_variants.filter(size=item.size).first().stock if item.product.size_variants.filter(size=item.size).exists() else 0
        
        context = {
            'items': user_cart,
            'items_count' : items_count,
        }
    else:
        context = {
            'items': [],
        }

    return render(request, 'cart.html', context)


def add_to_cart(request):
    if request.method == 'POST' and request.user.is_authenticated:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        size = data.get('size')
        quantity = data.get('quantity', 1)
        

        product = get_object_or_404(Product, id=product_id)


        cart, created = Cart.objects.get_or_create(user=request.user)

        existing_cart_item = CartItem.objects.filter(cart=cart, product=product, size=size).first()
        if existing_cart_item:
            return JsonResponse({
                'success': False,
                'message': f'Item with size {size} is already in your cart. You can update the quantity from the cart.'
            })

        new_cart_item = CartItem(cart=cart, product=product, size=size, quantity=int(quantity))
        new_cart_item.save()

        return JsonResponse({'success': True, 'message': 'Item added to cart'})

    return JsonResponse({'success': False, 'message': 'User not authenticated or invalid request'}, status=400)


def remove_item_from_cart(request):
    if request.method == 'POST':
        body = json.loads(request.body.decode('utf-8')) 
        item_id = body.get('itemId') 

        if item_id:
            cart_item = CartItem.objects.get(id=item_id)
            cart_item.delete()
            return JsonResponse({'success': True,'message': 'Item removed from the cart'})
        else:
            return JsonResponse({'success': False, 'message': 'Item ID not received.'})


def update_cart(request):

    return render(request,'cart.html')