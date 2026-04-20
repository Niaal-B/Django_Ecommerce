from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Address
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import re
from django.contrib.auth.hashers import check_password
from Order.models import Order,OrderItem
from Products.models import SizeVariant
from Wallet.models import Wallet, WalletTransaction
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

@login_required
def account(request):
    
    addresses = Address.objects.filter(user = request.user,is_deleted=False)
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    recent_transactions = WalletTransaction.objects.filter(wallet=wallet).order_by('-created_at')[:5]
    
    context = {
        'addresses' : addresses,
        'orders' : orders,
        'wallet': wallet,
        'recent_transactions': recent_transactions,
    }
    return render(request,'accounts.html',context)



@login_required
def update_profile(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        user = request.user

        errors = False
        
        # Username validation
        if not username:
            messages.error(request, 'Username is required.')
            errors = True
        elif len(username) < 3 or len(username) > 30:
            messages.error(request, 'Username must be between 3 and 30 characters.')
            errors = True
        elif not username.isalnum():
            messages.error(request, 'Username can only contain alphanumeric characters.')
            errors = True
        elif User.objects.filter(username=username).exclude(id=user.id).exists():
            messages.error(request, 'Username already taken.')
            errors = True

        # First name validation
        if not first_name or len(first_name) < 2:
            messages.error(request, 'First name must be at least 2 characters long.')
            errors = True
        elif not re.match(r"^[a-zA-Z\s-]+$", first_name):
            messages.error(request, 'First name can only contain letters, spaces, and hyphens.')
            errors = True

        # Last name validation
        if not last_name or len(last_name) < 2:
            messages.error(request, 'Last name must be at least 2 characters long.')
            errors = True
        elif not re.match(r"^[a-zA-Z\s-]+$", last_name):
            messages.error(request, 'Last name can only contain letters, spaces, and hyphens.')
            errors = True

        if not errors:
            try:
                user.username = username
                user.first_name = first_name
                user.last_name = last_name
                user.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('account')

            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')

    return redirect('account')




@login_required
def add_address(request):
    if request.method == 'POST':
        next_url = request.POST.get('next', 'account')
        name = request.POST.get('name')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        country = request.POST.get('country')
        postcode = request.POST.get('postcode')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        additional_info = request.POST.get('additional_info')

        # Validation for required fields
        if not name or not address or not city or not state or not country or not postcode or not phone:
            messages.error(request, 'All fields are required except additional info.')
            return redirect(next_url)

       
        if not postcode.isdigit():
            messages.error(request, 'Postcode must be numeric.')
            return redirect(next_url)

        
        phone_regex = re.compile(r'^\+?[1-9]\d{1,14}$')
        if not phone_regex.match(phone):
            messages.error(request, 'Invalid phone number format.')
            return redirect(next_url)

        
        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            messages.error(request, 'Invalid email address.')
            return redirect(next_url)

        
        try:
            Address.objects.create(
                user=request.user,
                name=name,
                address=address,
                city=city,
                state=state,
                country=country,
                postcode=postcode,
                phone=phone,
                email=email,
                additional_info=additional_info
            )
            messages.success(request, 'Address added successfully!')
        except Exception as e:
            logger.error(f"Error adding address for user {request.user.id}: {str(e)}", exc_info=True)
            messages.error(request, 'An error occurred while saving the address. Please try again.')
            return redirect(next_url)
        if not request.POST.get('next') or request.POST.get('next') == 'account':
            return redirect(f"{reverse('account')}?tab=address")
        return redirect(next_url) 

    return redirect('account') 


@login_required
def edit_address(request):
    if request.method == 'POST':
        next_url = request.POST.get('next', 'account')
        address_id = request.POST.get('id')
        address = get_object_or_404(Address, id=address_id)


        name = request.POST.get('name')
        address_line = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        country = request.POST.get('country')
        postcode = request.POST.get('postcode')
        phone = request.POST.get('phone')

        
        if not postcode.isdigit():
            messages.error(request, 'Postcode must be numeric.')
            return redirect(next_url)

       
        phone_regex = re.compile(r'^\+?[1-9]\d{1,14}$')
        if not phone_regex.match(phone):
            messages.error(request, 'Invalid phone number format.')
            return redirect(next_url)

        
        email = request.POST.get('account')
        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            messages.error(request, 'Invalid email address.')
            return redirect(next_url)

       
        try:
            address.name = name
            address.address = address_line
            address.city = city
            address.state = state
            address.country = country
            address.postcode = postcode
            address.phone = phone
            address.additional_info = request.POST.get('additional_info')

            address.save()
            messages.success(request, 'Address updated successfully.')
        except Exception as e:
            logger.error(f"Error editing address {address_id} for user {request.user.id}: {str(e)}", exc_info=True)
            messages.error(request, 'An error occurred while updating the address.')
            return redirect(next_url)
        if not request.POST.get('next') or request.POST.get('next') == 'account':
            return redirect(f"{reverse('account')}?tab=address")
        return redirect(next_url) 

    return redirect('account')



@login_required
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)

    if request.method == 'POST':
        try:
            address.is_deleted = True
            address.save()
            messages.success(request, 'Address deleted successfully!')
        except Exception as e:
            logger.error(f"Error deleting address {address_id} for user {request.user.id}: {str(e)}", exc_info=True)
            messages.error(request, 'An error occurred while deleting the address.')
        return redirect(f"{reverse('account')}?tab=address") 

    return redirect(f"{reverse('account')}?tab=address")





@login_required
def update_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        user = request.user


        if user.check_password(current_password):
            if password == confirm_password:
                try:
                    user.set_password(password)
                    user.save()
                    messages.success(request, 'Password updated successfully')
                except Exception as e:
                    logger.error(f"Error updating password for user {user.id}: {str(e)}", exc_info=True)
                    messages.error(request, 'An error occurred while updating your password.')
                return redirect('account')
            else:
                messages.error(request, 'Passwords do not match')
        else:
            messages.error(request, 'Old password is incorrect')

    return redirect('account')


@login_required
def view_order_items(request,order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order).select_related('size_variant')
    for item in order_items:
        item.total_price = item.quantity * item.price
     
    context = {
        'order' : order,
        'order_items' : order_items
    }
    return render(request, 'order_details.html', context)


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if not order.is_cancellable:
        if order.status == 'canceled':
            messages.error(request, "This order is already canceled.")
        else:
            messages.error(request, f"Cannot cancel order in '{order.get_status_display()}' status.")
        return redirect('account')

    try:
        with transaction.atomic():
            # Restore stock
            order_items = order.items.all()
            for item in order_items:
                if item.size_variant:
                    item.size_variant.stock += item.quantity
                    item.size_variant.save()

            # Update status and sync items
            order.status = 'canceled'
            order.save()
            order.sync_items_status()

            # Refund to Wallet if payment was made
            if order.payment_status == 'paid' or order.payment_method == 'razorpay':
                user_wallet, created = Wallet.objects.get_or_create(user=request.user)
                user_wallet.balance += order.total_price
                user_wallet.save()
                
                WalletTransaction.objects.create(
                    wallet=user_wallet,
                    amount=order.total_price,
                    transaction_type='CREDIT',
                    description=f"Refund for canceled Order #{order.id}"
                )
                messages.success(request, f"Order canceled. amount ₹{order.total_price} has been credited to your wallet.")
            else:
                messages.success(request, "Order has been successfully canceled.")
    except Exception as e:
        logger.error(f"Error canceling order {order_id} for user {request.user.id}: {str(e)}", exc_info=True)
        messages.error(request, "An error occurred while canceling the order. Please try again.")

    return redirect('account')

@login_required
def return_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == 'POST':
        if not order.is_returnable:
            messages.error(request, "This order cannot be returned.")
            return redirect('account')

        return_reason = request.POST.get('return_reason')
        if not return_reason:
            messages.error(request, "Please provide a reason for return.")
            return redirect('account')

        try:
            with transaction.atomic():
                order.status = 'returned'
                order.return_reason = return_reason
                order.save()
                
                # Sync all items to 'returned' status
                order.sync_items_status()

                # For now, credit wallet immediately on return (can be moved to admin approval later)
                if order.payment_status == 'paid' or order.payment_method == 'razorpay':
                    user_wallet, created = Wallet.objects.get_or_create(user=request.user)
                    user_wallet.balance += order.total_price
                    user_wallet.save()
                    
                    WalletTransaction.objects.create(
                        wallet=user_wallet,
                        amount=order.total_price,
                        transaction_type='CREDIT',
                        description=f"Refund for returned Order #{order.id}"
                    )
                    messages.success(request, f"Return request submitted. amount ₹{order.total_price} has been credited to your wallet.")
                else:
                    messages.success(request, f"Return request for Order #{order.id} has been submitted.")
        except Exception as e:
            logger.error(f"Error returning order {order_id} for user {request.user.id}: {str(e)}", exc_info=True)
            messages.error(request, "An error occurred while submitting the return request.")
        return redirect('account')

    return redirect('account')

@login_required
def cancel_order_item(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, order__user=request.user)
    order = item.order

    if not order.is_cancellable:
        messages.error(request, f"Cannot cancel item because the order is in '{order.get_status_display()}' status.")
        return redirect('view_order_items', order_id=order.id)

    if item.status == 'canceled':
        messages.error(request, "This item is already canceled.")
        return redirect('view_order_items', order_id=order.id)

    try:
        with transaction.atomic():
            # Change item status
            item.status = 'canceled'
            item.save()

            # Restore stock
            if item.size_variant:
                item.size_variant.stock += item.quantity
                item.size_variant.save()

            # Determine Refund
            if order.payment_status == 'paid' or order.payment_method == 'razorpay':
                refund_amount = (item.price * item.quantity) - item.discount
                user_wallet, created = Wallet.objects.get_or_create(user=request.user)
                user_wallet.balance += refund_amount
                user_wallet.save()
                
                WalletTransaction.objects.create(
                    wallet=user_wallet,
                    amount=refund_amount,
                    transaction_type='CREDIT',
                    description=f"Refund for canceled item ({item.product.name}) in Order #{order.id}"
                )
                messages.success(request, f"Item canceled. Amount ₹{refund_amount} has been credited to your wallet.")
            else:
                messages.success(request, f"Item '{item.product.name}' has been successfully canceled.")

            # Check if all items are canceled to update parent order status
            remaining_items = order.items.exclude(status='canceled')
            if not remaining_items.exists():
                order.status = 'canceled'
                order.save()
    except Exception as e:
        logger.error(f"Error canceling order item {item_id} for user {request.user.id}: {str(e)}", exc_info=True)
        messages.error(request, "An error occurred while canceling the item.")

    return redirect('view_order_items', order_id=order.id)

@login_required
def return_order_item(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, order__user=request.user)
    order = item.order

    if request.method == 'POST':
        if not order.is_returnable:
            messages.error(request, "This item cannot be returned because the order is not delivered.")
            return redirect('view_order_items', order_id=order.id)

        return_reason = request.POST.get('return_reason')
        if not return_reason:
            messages.error(request, "Please provide a reason for the return.")
            return redirect('view_order_items', order_id=order.id)

        if item.status == 'returned':
            messages.error(request, "This item has already been returned.")
            return redirect('view_order_items', order_id=order.id)
            
        if item.status == 'canceled':
            messages.error(request, "Cannot return a canceled item.")
            return redirect('view_order_items', order_id=order.id)

        try:
            with transaction.atomic():
                # Change item status to request
                item.status = 'return_requested'
                item.return_reason = return_reason
                item.save()

                messages.success(request, f"Return request for '{item.product.name}' has been submitted and is pending admin approval.")
        except Exception as e:
            logger.error(f"Error returning order item {item_id} for user {request.user.id}: {str(e)}", exc_info=True)
            messages.error(request, "An error occurred while processing your return request.")

    return redirect('view_order_items', order_id=order.id)