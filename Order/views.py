from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from decimal import Decimal
import razorpay
import json
from Account.models import Address,Wallet,WalletTransaction
from Cart.models import Cart, CartItem
from Products.models import Product, SizeVariant
from Coupon.models import Coupon
from .models import Order, OrderItem
from Adminauth.views import is_admin
import logging
from Order.models import Order




razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@login_required
def place_order(request):
    user = request.user
    addresses = Address.objects.filter(user=user)

    try:
        cart = Cart.objects.get(user=user)
        cart_items = CartItem.objects.filter(cart=cart,product__is_listed=True)

        if not cart_items.exists():
            return JsonResponse({"error": "Your cart is empty. Please add items to checkout."}, status=400)

        total = Decimal('0.00')
        for item in cart_items:
            price = Decimal(str(item.product.offer if item.product.offer else item.product.price))
            quantity = Decimal(str(item.quantity))
            item.subtotal = price * quantity
            total += item.subtotal
        
        delivery_charge = Decimal('40.00') if total < Decimal('500.00') else Decimal('0.00')
        total += delivery_charge


        if request.method == "POST":
            try:
                data = json.loads(request.body.decode("utf-8"))
                address_id = data.get("address_id")
                payment_method = data.get("payment_method")
                print("order placed")
                print(payment_method,"payment method")
                print(payment_method)
                coupon_code = data.get('coupon_code')
                wallet = Wallet.objects.get(user=request.user)
                print(coupon_code)



                if not address_id or not payment_method:
                    return JsonResponse({"error": "Address or payment method not provided."}, status=400)

                address = Address.objects.get(id=address_id, user=user)

                discount = Decimal('0.00')
                if coupon_code:
                    coupon = get_object_or_404(Coupon, code=coupon_code)
                    if coupon.usage_limit <= 0:
                        return JsonResponse({
                    'success': False,
                    'message': 'This coupon limit exceeded'
                })
                    discount = coupon.discount_value
                    total -=discount
                    coupon.usage_limit-=1
                    coupon.save() 
                if payment_method == 'COD'and total >1000:
                    return JsonResponse({"error": "Order above 1000 is not available for COD."}, status=400)
                if payment_method == "wallet" and total > wallet.balance:
                    return JsonResponse({"error": "Not Enough money in Wallet Try Another Payment method"}, status=400)

                for item in cart_items:
                        size_variant = SizeVariant.objects.get(product=item.product, size=item.size)
                        if size_variant.stock < item.quantity:
                            return JsonResponse({"error": f"Not enough stock for {item.product.name} (Size: {item.size})."}, status=400)



                order = Order.objects.create(
                    user=user,
                    address=address,
                    payment_method=payment_method,
                    total_price=total,
                    coupon_code=coupon_code if coupon_code else '',
                    discount=discount,
                    status="Pending",
                )
                print("order created")



                if payment_method == 'razorpay':
                    try:
                        for item in cart_items:
                            try:
                                size_variant = SizeVariant.objects.get(product=item.product, size=item.size)

                                size_variant.stock -= int(item.quantity)
                                size_variant.save()

                                price = item.product.offer if item.product.offer and item.product.offer > 0 else item.product.price
                                discount = (item.product.price - price) * quantity if item.product.offer else Decimal('0.00') 
                                OrderItem.objects.create(
                                    order=order,
                                    product=item.product,
                                    quantity=item.quantity,
                                    price=price,
                                    size_variant=size_variant,
                                    discount=discount
                        
                                )
                            except SizeVariant.DoesNotExist:
                                return JsonResponse({"error": f"Size variant not found for {item.product.name} (Size: {item.size})."}, status=400)

                        cart_items.delete()                       
                        
                        currency = 'INR'
                        amount = int(total * 100) 

                       
                        razorpay_order = razorpay_client.order.create({
                            'amount': amount,
                            'currency': currency,
                            'payment_capture': '1'
                        })

                       
                        order.razorpay_order_id = razorpay_order['id']
                        order.save()

                        payment_data = {
                            'order_id': razorpay_order['id'],
                            'amount': amount,
                            'currency': currency,
                            'key': settings.RAZORPAY_KEY_ID,
                            'success': True
                        }
                        return JsonResponse(payment_data)

                    except Exception as e:
                        return JsonResponse({
                            'error': f'Error initializing Razorpay payment: {str(e)}'
                        }, status=400)

                if payment_method == 'COD':
                    order.payment_status = 'Pending'
                    order.save()
                if payment_method == "wallet":
                    order.payment_status = 'Completed'
                    order.save()
                    wallet = Wallet.objects.get(user=request.user)

                    wallet.balance-=total
                    wallet.save()
                    WalletTransaction.objects.create(
                    wallet=wallet,
                    amount=total,
                    transaction_type='DEBIT',
                    description=f"Purchased for Order #{order.id}"
                )
                   
                for item in cart_items:
                    try:
                        size_variant = SizeVariant.objects.get(product=item.product, size=item.size)
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
                print("this is order id :",order.id)
                return JsonResponse({"success": "Order placed successfully!","order_id": order.id}, status=200)

            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid request format."}, status=400)

    except Cart.DoesNotExist:
        return JsonResponse({"error": "Cart does not exist."}, status=400)

    context = {
        'addresses': addresses,
        'cart_items': cart_items,
        'total': total,
        'delivery_charge': delivery_charge
    }
    return render(request, 'checkout.html', context)


def order_success(request):
    order_id = request.GET.get('order_id')
    order = get_object_or_404(Order,id=order_id)
    print(order)
    context = {
        "order" : order
        
    }
    return render(request, 'order_confirm.html',context)


@user_passes_test(is_admin)
def order_management(request):
    orders = Order.objects.all().order_by('-created_at')
    context = {'orders': orders}
    return render(request, 'admin/order_admin.html', context)


def admin_order_details(request, order_id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('admin_login')

    order = get_object_or_404(Order, id=order_id)
    order_items = order.items.all()
    for item in order_items:
        item.subtotal = item.quantity * item.price

    context = {
        'order': order,
        'order_items': order_items
    }
    return render(request, 'admin/order_details_admin.html', context)


from django.shortcuts import get_object_or_404, redirect
from .models import Order, OrderItem

def manage_order_status(request, order_id):
    if request.method == "POST":
        status = request.POST.get("order_status")  
        order = get_object_or_404(Order, id=order_id)  
        if status:
            print(status)
            order.status = status
            if status == "delivered" or status == "Delivered":
                order.payment_status = "completed" 
            if status == "Approve Returned":
                print("this block worked")
                user = order.user
                wallet, created = Wallet.objects.get_or_create(user=user)
                print(wallet)
                print(order.total_price)
                wallet.balance += order.total_price
                wallet.save()
                WalletTransaction.objects.create(
                wallet=wallet,
                amount=order.total_price,
                transaction_type='CREDIT',
                description=f"Refund for Order #{order.id}"
            )


            order.save()
            

            order_items = order.items.all()  
            for item in order_items:
                item.status = status  
                item.save()
    
    return redirect('order-view', order_id)  





logger = logging.getLogger(__name__)


razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@csrf_exempt
@require_POST
def paymenthandler(request):
    """Handle Razorpay payment verification and order processing"""
    try:
        
        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')

       
        logger.info(f"Received payment verification request - Order ID: {order_id}, Payment ID: {payment_id}")
        
        
        if not all([payment_id, order_id, signature]):
            logger.error(f"Missing payment parameters: payment_id={bool(payment_id)}, order_id={bool(order_id)}, signature={bool(signature)}")
            return JsonResponse({
                'error': 'Missing required payment parameters',
                'received_params': {
                    'payment_id': payment_id,
                    'order_id': order_id,
                    'signature': signature
                }
            }, status=400)
        
        
        params_dict = {
            'razorpay_payment_id': payment_id,
            'razorpay_order_id': order_id,
            'razorpay_signature': signature
        }
        
        try:
            razorpay_client.utility.verify_payment_signature(params_dict)
            
            
            try:
                order = Order.objects.get(razorpay_order_id=order_id)
                
            
                payment = razorpay_client.payment.fetch(payment_id)
                
                
                if int(payment['amount']) != int(order.total_price * 100):
                    logger.error(f"Payment amount mismatch - Expected: {int(order.total_price * 100)}, Received: {payment['amount']}")
                    return JsonResponse({
                        'error': 'Payment amount does not match order amount'
                    }, status=400)
                
               
                order.payment_id = payment_id
                order.payment_status = 'Completed'
                order.save()
                
               
                return JsonResponse({
                    'success': True,
                    'message': 'Payment successful',
                    'order_id': order_id
                })
                
            except Order.DoesNotExist:
                logger.error(f"Order not found: {order_id}")
                return JsonResponse({
                    'error': 'Order not found'
                }, status=400)
                
        except razorpay.errors.SignatureVerificationError as e:
            logger.error(f"Signature verification failed: {str(e)}")
            return JsonResponse({
                'error': 'Invalid payment signature'
            }, status=400)
            
    except Exception as e:
        logger.error(f"Payment processing error: {str(e)}")
        return JsonResponse({
            'error': 'Payment processing failed',
            'details': str(e)
        }, status=500)