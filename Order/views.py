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
    order_items = order.items.all()
    for items in order_items:
        items.subtotal = items.quantity * items.price

    
    context = {
        'order': order,
        'order_items': order_items
    }
    return render(request, 'admin/order_details_admin.html', context)
