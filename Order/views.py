from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from decimal import Decimal
import json
import razorpay
import logging

from Account.models import Address
from Cart.models import Cart, CartItem
from .models import Order, OrderItem
from Products.models import Product, SizeVariant
from Adminauth.views import is_admin 

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
        
       
        delivery_charge = settings.DELIVERY_CHARGE if total < settings.FREE_SHIPPING_THRESHOLD else Decimal('0.00')
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
            
            
            if payment_method == 'COD' and total > settings.MAX_COD_AMOUNT:
                return JsonResponse({"error": f"Cash on Delivery is not available for orders above ₹{settings.MAX_COD_AMOUNT}."}, status=400)

            if payment_method == "razorpay":
                # Validate API keys
                if not settings.RAZOR_KEY_ID or not settings.RAZOR_KEY_SECRET:
                    return JsonResponse({"error": "Payment gateway not configured. Please contact support."}, status=503)
                
                
                try:
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

                    # Create Pending Order before returning to frontend
                    order = Order.objects.create(
                        user=user,
                        address=address,
                        payment_method="razorpay",
                        total_price=total,
                        payment_status="Pending",
                        razorpay_order_id=razorpay_order_id
                    )

                    for item in cart_items:
                        OrderItem.objects.create(
                            order=order,
                            product=item.product,
                            quantity=item.quantity,
                            price=item.product.offer if item.product.offer and item.product.offer > 0 else item.product.price,
                            size_variant=SizeVariant.objects.get(product=item.product, size=item.size),
                            status="Pending"
                        )

                    context = {
                        'razorpay_order_id': razorpay_order_id,
                        'razorpay_merchant_key': settings.RAZOR_KEY_ID,
                        'razorpay_amount': payment_amount,
                        'currency': currency,
                        'address_id': address_id,
                        'payment_method': "razorpay",
                        'order_id': order.id # internal id for easier lookup
                    }
                    return JsonResponse(context)
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Failed to initiate Razorpay order: {str(e)}", exc_info=True)
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
        # Handle both JSON (AJAX) and POST Form Data (Razorpay Callback)
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST

            razorpay_payment_id = data.get('razorpay_payment_id')
            razorpay_order_id = data.get('razorpay_order_id')
            razorpay_signature = data.get('razorpay_signature')
            
            # address_id might come from query param if we added it to callback_url
            address_id = data.get('address_id') or request.GET.get('address_id')
            
            # Validate required fields
            if not all([razorpay_payment_id, razorpay_order_id, razorpay_signature]):
                return JsonResponse({'error': 'Missing required payment fields'}, status=400)

            # Validate API keys
            if not settings.RAZOR_KEY_ID or not settings.RAZOR_KEY_SECRET:
                return JsonResponse({'error': 'Payment gateway not configured'}, status=503)

            client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
            
            # Verify Signature
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            client.utility.verify_payment_signature(params_dict)

            # Find the existing pending order
            try:
                order = Order.objects.get(razorpay_order_id=razorpay_order_id, user=request.user)
                
                # If already marked as Paid (e.g., by webhook), just redirect/success
                if order.payment_status == "Paid":
                    if request.content_type == 'application/json':
                        return JsonResponse({'success': 'Order already processed'})
                    return redirect('order_success')

                # Update Order to Confirmed
                order.payment_status = "Paid"
                order.payment_id = razorpay_payment_id
                order.status = "confirmed"
                order.save()

                # Deduct stock and finalize items
                for item in order.items.all():
                    if item.size_variant:
                        item.size_variant.stock -= item.quantity
                        item.size_variant.save()

                # Clear User's Cart
                try:
                    cart = Cart.objects.get(user=request.user)
                    CartItem.objects.filter(cart=cart).delete()
                except Cart.DoesNotExist:
                    pass

                if request.content_type == 'application/json':
                    return JsonResponse({'success': 'Payment successful and order placed!'})
                return redirect('order_success')

            except Order.DoesNotExist:
                return JsonResponse({'error': 'Order not found'}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            logging.error(f"Payment success error: {str(e)}", exc_info=True)
            if request.content_type == 'application/json':
                return JsonResponse({'error': f'Payment verification failed: {str(e)}'}, status=400)
            return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)
            
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def razorpay_webhook(request):
    if request.method == "POST":
        # Get the webhook signature from the headers
        webhook_signature = request.headers.get('X-Razorpay-Signature')
        webhook_secret = settings.RAZOR_WEBHOOK_SECRET
        
        if not webhook_secret:
            logging.error("RAZOR_WEBHOOK_SECRET not set in settings")
            return JsonResponse({'error': 'Webhook secret not configured'}, status=500)

        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
        
        try:
            # Verify the webhook signature
            payload = request.body.decode('utf-8')
            client.utility.verify_webhook_signature(payload, webhook_signature, webhook_secret)
            
            data = json.loads(payload)
            event = data.get('event')
            
            # Handle payment.captured or order.paid
            if event in ['payment.captured', 'order.paid']:
                payment_id = data['payload']['payment']['entity']['id']
                razorpay_order_id = data['payload']['payment']['entity']['order_id']
                
                try:
                    order = Order.objects.get(razorpay_order_id=razorpay_order_id)
                    if order.payment_status != "Paid":
                        order.payment_status = "Paid"
                        order.payment_id = payment_id
                        order.status = "confirmed"
                        order.save()
                        
                        # Decrease stock for items in this order
                        for item in order.items.all():
                            if item.size_variant:
                                item.size_variant.stock -= item.quantity
                                item.size_variant.save()
                        
                        # Clear cart for the user who placed the order
                        try:
                            cart = Cart.objects.get(user=order.user)
                            CartItem.objects.filter(cart=cart).delete()
                        except Cart.DoesNotExist:
                            pass
                            
                except Order.DoesNotExist:
                    logging.error(f"Order with razorpay_order_id {razorpay_order_id} not found during webhook")
            
            return JsonResponse({'status': 'ok'})
            
        except Exception as e:
            logging.error(f"Webhook processing error: {str(e)}", exc_info=True)
            return JsonResponse({'error': str(e)}, status=400)
            
    return JsonResponse({'error': 'Invalid request method'}, status=400)
