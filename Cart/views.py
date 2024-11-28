from django.shortcuts import render,redirect,get_object_or_404
from django.http import JsonResponse
import json
from .models import Cart,CartItem
from Products.models import Product
from decimal import Decimal
from Wishlist.models import Wishlist


# Create your views here.
def cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        user_cart = CartItem.objects.filter(cart__user=request.user, product__is_listed=True)
        items_count = user_cart.count()
        if request.method == 'POST':
            for item in CartItem.objects.filter(cart=request.user.cart):
                quantity = request.POST.get(f'quantity_{item.id}')
                print(quantity)
                if quantity:
                    item.quantity = int(float(quantity))  
                    item.save()
                    
        total = Decimal('0.00')
        for item in user_cart:
            item.stock = item.product.size_variants.filter(size=item.size).first().stock if item.product.size_variants.filter(size=item.size).exists() else 0
            price = Decimal(str(item.product.offer if item.product.offer else item.product.price))
            quantity = Decimal(str(item.quantity))
            item.subtotal = price * quantity
            total += item.subtotal 

        delivery_charge = Decimal('40.00') if total < Decimal('500.00') else Decimal('0.00')
        total += delivery_charge   

        context = {
            'items': user_cart,
            'items_count' : items_count,
            'total': total,
        'delivery_charge': delivery_charge
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

def wishlist_add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        
        size = request.POST.get('size')
        quantity = request.POST.get('quantity', 1)

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
        wishlist_item = Wishlist.objects.filter(user=request.user, product=product, size=size).first()
        print(wishlist_item)
        if wishlist_item:
            wishlist_item.delete()
        return JsonResponse({'success': True, 'message': 'Item added to cart'})

    return JsonResponse({'success': False, 'message': 'User not authenticated or invalid request'}, status=400)
