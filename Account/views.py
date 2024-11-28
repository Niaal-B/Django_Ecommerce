from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Address,Wallet,WalletTransaction
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import re
from django.contrib.auth.hashers import check_password
from Order.models import Order,OrderItem
from Products.models import SizeVariant
from django.db.models import F

# Create your views here.
@login_required
def account(request):
    
    addresses = Address.objects.filter(user = request.user,is_deleted=False)
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    transactions = WalletTransaction.objects.filter(wallet=wallet).order_by('-created_at')[:10]

    
    context = {
        'addresses' : addresses,
        'orders' : orders,
        'wallet_balance': wallet.balance,
        'transactions': transactions,
    }
    return render(request,'accounts.html',context)



@login_required
def update_username(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        user = request.user

        
        if len(username) < 3 or len(username) > 30:
            messages.error(request, 'Username must be between 3 and 30 characters.')
        elif not username.isalnum():
            messages.error(request, 'Username can only contain alphanumeric characters.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
        else:
            try:
                validator = RegexValidator(r'^[a-zA-Z0-9]*$', 'Username must be alphanumeric.')
                validator(username)
                
                user.username = username
                user.save()
                request.session['username'] = username 
                messages.success(request, 'Username updated successfully!')
            
                return redirect('account')

            except ValidationError as e:
                messages.error(request, f'Invalid username: {e.message}')

    return render(request, 'accounts.html')




@login_required
def add_address(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        country = request.POST.get('country')
        postcode = request.POST.get('postcode')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        additional_info = request.POST.get('additional_info')
        next_url = request.POST.get('next', '/checkout/')

        # Validation for required fields
        if not name or not address or not city or not state or not country or not postcode or not phone:
            messages.error(request, 'All fields are required except additional info.')
            return redirect('account')

       
        if not postcode.isdigit():
            messages.error(request, 'Postcode must be numeric.')
            return redirect('account')

        
        phone_regex = re.compile(r'^\+?[1-9]\d{1,14}$')
        if not phone_regex.match(phone):
            messages.error(request, 'Invalid phone number format.')
            return redirect('account')

        
        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            messages.error(request, 'Invalid email address.')
            return redirect('account')

        
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
        return redirect(next_url) 

    return redirect('account') 


@login_required
def edit_address(request):
    if request.method == 'POST':
        address_id = request.POST.get('id')
        address = get_object_or_404(Address, id=address_id)
        print(address_id,"address id yaan")

        name = request.POST.get('name')
        address_line = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        country = request.POST.get('country')
        postcode = request.POST.get('postcode')
        phone = request.POST.get('phone')
        print(name)
        print(address_line)
        print(city)
        print(state)
        print(country)
        print(postcode)
        print(phone)
        
        if not postcode.isdigit():
            messages.error(request, 'Postcode must be numeric.')
            return redirect('account')

       
        phone_regex = re.compile(r'^\+?[1-9]\d{1,14}$')
        if not phone_regex.match(phone):
            messages.error(request, 'Invalid phone number format.')
            return redirect('account')

        
        email = request.POST.get('account')
        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            messages.error(request, 'Invalid email address.')
            return redirect('account')

       
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
        return redirect('account') 

    return redirect('account')



@login_required
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)

    if request.method == 'POST':
        address.is_deleted = True
        messages.success(request, 'Address deleted successfully!')
        return redirect('account') 


    return redirect('account')





@login_required
def update_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        user = request.user


        if user.check_password(current_password):
            if password == confirm_password:
                user.set_password(password)
                user.save()
                messages.success(request, 'Password updated successfully')
                return redirect('account')
            else:
                messages.error(request, 'Passwords do not match')
        else:
            messages.error(request, 'Old password is incorrect')

    return redirect('account')


@login_required
def view_order_items(request,order_id):
    order = Order.objects.get(id=order_id,user=request.user)
    order_items = OrderItem.objects.filter(order=order).select_related('size_variant')
    print(order_items)
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

    if order.status == 'Canceled':
        messages.error(request, "This order is already canceled.")
        return redirect('account') 
    if order.payment_method == 'razorpay' and order.payment_status == 'Completed':
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        

        wallet.balance += order.total_price
        wallet.save()


        WalletTransaction.objects.create(
            wallet=wallet,
            amount=order.total_price,
            transaction_type='CREDIT',
            description=f"Refund for Order #{order.id}"
        )

        
    if order.payment_method == 'wallet' and order.payment_status == 'Completed':
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        

        wallet.balance += order.total_price
        wallet.save()


        WalletTransaction.objects.create(
            wallet=wallet,
            amount=order.total_price,
            transaction_type='CREDIT',
            description=f"Refund for Order #{order.id}"
        )



    order_items = OrderItem.objects.filter(order=order)
    for item in order_items:
        size_variant = item.size_variant
        size_variant.stock += item.quantity
        size_variant.save()


    order.status = 'Canceled'
    order.save()

    messages.success(request, "Order has been successfully canceled.")
    return redirect('account')

def request_return(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        return_reason = request.POST.get('return_reason')
        order = get_object_or_404(Order, id=order_id, user=request.user)
    
        if order.status == "Delivered":
            order.status = "requested_return"
            order.return_reason = return_reason
            order.save()
    return redirect('account')

def cancel_item_order(request):
    if request.method =='POST':
        variant_id = request.POST.get('variant_id')
        order_id = request.POST.get("order_id") 
        item = get_object_or_404(OrderItem,size_variant=variant_id,order=order_id)
        order = get_object_or_404(Order,id=order_id)

        
        size_variant = get_object_or_404(SizeVariant, id=variant_id)
        print(size_variant.stock)
        print(item.quantity)
        size_variant.stock = F('stock') + item.quantity  
        size_variant.save()       
        order.total_price = F('total_price') - item.price * item.quantity
        order.save()
        item.delete()
        print(variant_id)
    return redirect('view_order_items', order_id=order_id)



@login_required
def add_money_to_wallet(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
                
            wallet = Wallet.objects.get(user=request.user)
            wallet.balance += amount
            wallet.save()
            
         
            WalletTransaction.objects.create(
                wallet=wallet,
                amount=amount,
                transaction_type='CREDIT',
                description='Added money to wallet'
            )
            
            messages.success(request, f'Successfully added ₹{amount} to your wallet')
        except (ValueError, TypeError):
            messages.error(request, 'Please enter a valid amount')
        
    return redirect('account')