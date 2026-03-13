from django.shortcuts import render, redirect,get_object_or_404
from Account.models import Address
from Cart.models import Cart, CartItem
from decimal import Decimal
from .models import Order,OrderItem
from Products.models import Product,SizeVariant
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import user_passes_test
from Adminauth.views import is_admin 
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt


from decimal import Decimal
import json
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def place_order(request):
    user = request.user
    addresses = Address.objects.filter(user=user)
    
    try:
        cart = Cart.objects.get(user=user)
        cart_items = CartItem.objects.filter(cart=cart)
        
      
        if not cart_items.exists():
            return JsonResponse({"error": "Your cart is empty. Please add items to checkout."}, status=400)

    
        for item in cart_items:
            if item.quantity < 1:
                return JsonResponse({"error": f"Invalid quantity for {item.product.name}. Please update your cart."}, status=400)
            
           
            size_variant = SizeVariant.objects.get(product=item.product, size=item.size)
            if item.quantity > size_variant.stock:
                return JsonResponse({
                    "error": f"Requested quantity for {item.product.name} (Size: {item.size}) exceeds available stock."
                }, status=400)
        
        
        total = Decimal('0.00')
        for item in cart_items:
            price = Decimal(str(item.product.offer if item.product.offer else item.product.price))
            quantity = Decimal(str(item.quantity))
            item.subtotal = price * quantity
            total += item.subtotal
        
       
        delivery_charge = Decimal('40.00') if total < Decimal('500.00') else Decimal('0.00')
        total += delivery_charge
        
    except Cart.DoesNotExist:
        cart_items = []
        total = Decimal('0.00')
        delivery_charge = Decimal('0.00')
    
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            address_id = data.get("address_id")
            payment_method = data.get("payment_method")

          
            if not address_id or not payment_method:
                return JsonResponse({"error": "Address or payment method not provided."}, status=400)

           
            address = Address.objects.get(id=address_id, user=request.user)
            
            
            if payment_method == 'COD' and total > 1000:
                return JsonResponse({"error": "Cash on Delivery is not available for orders above ₹1000."}, status=400)

            if payment_method == "razorpay":
                # Validate API keys
                if not settings.RAZOR_KEY_ID or not settings.RAZOR_KEY_SECRET:
                    return JsonResponse({"error": "Payment gateway not configured. Please contact support."}, status=503)
                
                try:
                    import razorpay
                except ImportError as e:
                    return JsonResponse({"error": f"Payment gateway not available: {str(e)}"}, status=503)
                
                try:
                    # Diagnostic logging (Safe: only logs the prefix)
                    key_id = settings.RAZOR_KEY_ID or ""
                    key_type = "TEST" if key_id.startswith("rzp_test_") else "LIVE" if key_id.startswith("rzp_live_") else "UNKNOWN/EMPTY"
                    print(f"DEBUG: Initializing Razorpay setup with {key_type} key (starts with: {key_id[:8]})")
                    
                    client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
                    payment_amount = int(total * 100)
                    currency = "INR"
                    
                    payment_data = {
                        "amount": payment_amount,
                        "currency": currency,
                        "payment_capture": "1"
                    }
                    
                    razorpay_order = client.order.create(data=payment_data)
                    razorpay_order_id = razorpay_order['id']

                    context = {
                        'razorpay_order_id': razorpay_order_id,
                        'razorpay_merchant_key': settings.RAZOR_KEY_ID,
                        'razorpay_key_prefix': (settings.RAZOR_KEY_ID or "")[:12],
                        'razorpay_amount': payment_amount,
                        'currency': currency,
                        'address_id': address_id,
                        'payment_method': "razorpay",
                    }
                    return JsonResponse(context)
                except Exception as e:
                    return JsonResponse({"error": f"Failed to create payment order: {str(e)}"}, status=500)

            # Create Order for COD
            order = Order.objects.create(
                user=user,
                address=address,
                payment_method=payment_method,
                total_price=total,
            )

            
            for item in cart_items:
                try:
                    size_variant = SizeVariant.objects.get(product=item.product, size=item.size)
                    if size_variant.stock < item.quantity:
                        return JsonResponse({"error": f"Not enough stock for {item.product.name} (Size: {item.size})."}, status=400)

                  
                    size_variant.stock -= int(item.quantity)
                    size_variant.save()

                   
                    price = item.product.offer if item.product.offer and item.product.offer > 0 else item.product.price
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=price,
                        size_variant=size_variant
                    )
                except SizeVariant.DoesNotExist:
                    return JsonResponse({"error": f"Size variant not found for {item.product.name} (Size: {item.size})."}, status=400)

           
            cart_items.delete()

            return JsonResponse({"success": "Order placed successfully!"}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid request format."}, status=400)
    
    
    context = {
        'addresses': addresses,
        'cart_items': cart_items,
        'total': total,
        'delivery_charge': delivery_charge
    }
    return render(request, 'checkout.html', context)


def order_success(request):
    return render(request,'order_confirm.html')

@user_passes_test(is_admin)
def order_management(request):
    orders = Order.objects.all().order_by('-created_at')
    context = {
        'orders' : orders
    }
    return render(request,'admin/order_admin.html',context)

def admin_order_details(request, order_id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('admin_login') 

    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        for key, value in request.POST.items():
            if key.startswith("status_"):
                try:
                    item_id = key.split("_")[1]
                    item = OrderItem.objects.get(id=item_id, order=order)
                    item.status = value
                    item.save()
                except (IndexError, OrderItem.DoesNotExist, ValueError):
                    continue
        return redirect('order-view', order_id=order_id)

    order_items = order.items.all()
    for items in order_items:
        items.subtotal = items.quantity * items.price

    
    context = {
        'order': order,
        'order_items': order_items
    }
    return render(request, 'admin/order_details_admin.html', context)

@csrf_exempt
@login_required
def payment_success(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            razorpay_payment_id = data.get('razorpay_payment_id')
            razorpay_order_id = data.get('razorpay_order_id')
            razorpay_signature = data.get('razorpay_signature')
            address_id = data.get('address_id')
            
            # Validate required fields
            if not razorpay_payment_id:
                return JsonResponse({'error': 'Missing razorpay_payment_id'}, status=400)
            if not razorpay_order_id:
                return JsonResponse({'error': 'Missing razorpay_order_id'}, status=400)
            if not razorpay_signature:
                return JsonResponse({'error': 'Missing razorpay_signature'}, status=400)
            if not address_id:
                return JsonResponse({'error': 'Missing address_id'}, status=400)
            
            # Validate API keys
            if not settings.RAZOR_KEY_ID or not settings.RAZOR_KEY_SECRET:
                return JsonResponse({'error': 'Payment gateway not configured'}, status=503)

            try:
                import razorpay
            except ImportError as e:
                return JsonResponse({'error': f'Payment gateway not available: {str(e)}'}, status=503)
            
            client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
            
            # Verify Signature
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            
            try:
                client.utility.verify_payment_signature(params_dict)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Payment signature verification failed: {str(e)}")
                return JsonResponse({'error': f'Payment verification failed: {str(e)}'}, status=400)

            # Get User and Address
            user = request.user
            try:
                address = Address.objects.get(id=address_id, user=user)
            except Address.DoesNotExist:
                return JsonResponse({'error': 'Address not found'}, status=404)
            
            # Calculate Total from Cart again to be safe
            try:
                cart = Cart.objects.get(user=user)
                cart_items = CartItem.objects.filter(cart=cart)
            except Cart.DoesNotExist:
                return JsonResponse({'error': 'Cart not found'}, status=404)
            
            if not cart_items.exists():
                return JsonResponse({'error': 'Cart is empty'}, status=400)
            
            total = Decimal('0.00')
            for item in cart_items:
                price = Decimal(str(item.product.offer if item.product.offer and item.product.offer > 0 else item.product.price))
                item.subtotal = price * Decimal(str(item.quantity))
                total += item.subtotal
                
            delivery_charge = Decimal('40.00') if total < Decimal('500.00') else Decimal('0.00')
            total += delivery_charge

            # Create Order
            order = Order.objects.create(
                user=user,
                address=address,
                payment_method="razorpay",
                total_price=total,
                payment_status="Paid",
                payment_id=razorpay_payment_id,
                razorpay_order_id=razorpay_order_id
            )

            # Create Order Items and Decrease Stock
            for item in cart_items:
                try:
                    size_variant = SizeVariant.objects.get(product=item.product, size=item.size)
                    if size_variant.stock < item.quantity:
                        # Rollback order if stock insufficient
                        order.delete()
                        return JsonResponse({'error': f'Insufficient stock for {item.product.name}'}, status=400)
                    
                    size_variant.stock -= int(item.quantity)
                    size_variant.save()

                    price = item.product.offer if item.product.offer and item.product.offer > 0 else item.product.price
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=price,
                        size_variant=size_variant,
                        status="Pending",
                        discount=0.00
                    )
                except SizeVariant.DoesNotExist:
                    order.delete()
                    return JsonResponse({'error': f'Size variant not found for {item.product.name}'}, status=404)

            # Clear Cart
            cart_items.delete()

            return JsonResponse({'success': 'Payment successful and order placed!'})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Payment success error: {str(e)}", exc_info=True)
            return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)
            
    return JsonResponse({'error': 'Invalid request method'}, status=400)
