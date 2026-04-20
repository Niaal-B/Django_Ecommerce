from django.shortcuts import render,redirect,get_object_or_404
from django.http import JsonResponse
import json
from .models import Cart,CartItem
from Products.models import Product
from Order.models import Coupon
from django.contrib import messages
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

def cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        user_cart = cart.items.all()
        items_count = user_cart.count()
        if request.method == 'POST':
            for item in CartItem.objects.filter(cart=request.user.cart):
                quantity = request.POST.get(f'quantity_{item.id}')

                if quantity:
                    try:
                        item.quantity = max(1, int(float(quantity)))  
                        item.save()
                    except (ValueError, TypeError):
                        messages.warning(request, f"Invalid quantity for {item.product.name}. Skipping update.")
                    except Exception as e:
                        logger.error(f"Error saving cart item {item.id}: {str(e)}", exc_info=True)
                    
        total_price = sum(item.total_price() for item in user_cart)
        
        # Coupon Logic
        coupon_id = request.session.get('coupon_id')
        discount = 0
        coupon = None
        if coupon_id:
            try:
                coupon = Coupon.objects.get(id=coupon_id, active=True)
                if total_price >= coupon.min_purchase_amount:
                    discount = coupon.discount_value
                else:
                    messages.warning(request, f"Coupon removed because minimum purchase amount is {coupon.min_purchase_amount}")
                    del request.session['coupon_id']
                    coupon = None
            except Coupon.DoesNotExist:
                del request.session['coupon_id']
        
        grand_total = max(0, float(total_price) - float(discount))

        for item in user_cart:
            item.stock = item.product.size_variants.filter(size=item.size).first().stock if item.product.size_variants.filter(size=item.size).exists() else 0
        
        context = {
            'items': user_cart,
            'items_count' : items_count,
            'total_price': total_price,
            'discount': discount,
            'grand_total': grand_total,
            'coupon': coupon,
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

        try:
            new_cart_item = CartItem(cart=cart, product=product, size=size, quantity=int(float(quantity)))
            new_cart_item.save()
            return JsonResponse({'success': True, 'message': 'Item added to cart'})
        except (ValueError, TypeError):
            return JsonResponse({'success': False, 'message': 'Invalid quantity received'}, status=400)
        except Exception as e:
            logger.error(f"Error adding to cart for user {request.user.id}: {str(e)}", exc_info=True)
            return JsonResponse({'success': False, 'message': 'An error occurred while adding to cart'}, status=500)

    return JsonResponse({'success': False, 'message': 'User not authenticated or invalid request'}, status=400)


def remove_item_from_cart(request):
    if request.method == 'POST':
        body = json.loads(request.body.decode('utf-8')) 
        item_id = body.get('itemId') 

        if item_id:
            try:
                cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
                cart_item.delete()
                return JsonResponse({'success': True,'message': 'Item removed from the cart'})
            except Exception as e:
                logger.error(f"Error removing item {item_id} from cart: {str(e)}", exc_info=True)
                return JsonResponse({'success': False, 'message': 'An error occurred while removing the item.'}, status=500)
        else:
            return JsonResponse({'success': False, 'message': 'Item ID not received.'})


def update_cart(request):

    return render(request,'cart.html')

def apply_coupon(request):
    referer = request.META.get('HTTP_REFERER', 'cart')
    if request.method == 'POST':
        code = request.POST.get('coupon_code')
        if not code:
            messages.error(request, "Please enter a valid coupon code.")
            return redirect(referer)
            
        try:
            coupon = Coupon.objects.get(code__iexact=code, active=True)
            
            # Use local date for comparisons
            curr_date = timezone.now().date()
            if not (coupon.valid_from <= curr_date <= coupon.valid_to):
                messages.error(request, "This coupon is expired or not yet valid.")
                return redirect(referer)
            
            if coupon.used_count >= coupon.usage_limit:
                messages.error(request, "This coupon's usage limit has been reached.")
                return redirect(referer)
                
            cart = Cart.objects.get(user=request.user)
            total_price = sum(item.total_price() for item in cart.items.all())
            
            if total_price < coupon.min_purchase_amount:
                messages.error(request, f"Minimum purchase amount of {coupon.min_purchase_amount} required.")
                return redirect(referer)
                
            request.session['coupon_id'] = coupon.id
            messages.success(request, f"Coupon {coupon.code} applied successfully!")
            
        except Coupon.DoesNotExist:
            messages.error(request, "Invalid coupon code.")
            
    return redirect(referer)

def remove_coupon(request):
    referer = request.META.get('HTTP_REFERER', 'cart')
    if 'coupon_id' in request.session:
        del request.session['coupon_id']
        messages.success(request, "Coupon removed.")
    return redirect(referer)