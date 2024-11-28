from django.shortcuts import render,redirect
from Adminauth.views import is_admin 
from django.contrib.auth.decorators import user_passes_test
from . models import Coupon
from datetime import datetime
from datetime import date
from django.contrib import messages
from Cart.models import Cart,CartItem
from django.utils import timezone
from decimal import Decimal
from django.http import JsonResponse
import json
from django.shortcuts import get_object_or_404

# Create your views here.
@user_passes_test(is_admin)
def coupon_management(request):
    coupons = Coupon.objects.all()
    context = {
        'coupons' : coupons
    }

    return render(request,'admin/coupon_admin.html',context)

def create_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        discount_value = request.POST.get('discount_value')
        min_purchase_amount = request.POST.get('min_purchase_amount')
        valid_from = request.POST.get('valid_from')
        valid_to = request.POST.get('valid_to')
        usage_limit = request.POST.get('usage_limit')

        if not code or not discount_value or not min_purchase_amount or not valid_from or not valid_to or not usage_limit:
            messages.error(request, "All fields are required.")
            return redirect('coupon_management')


        discount_value = float(discount_value)
        min_purchase_amount = float(min_purchase_amount)
        usage_limit = int(usage_limit)
        if discount_value <= 0:
                messages.error(request, "Discount value must be greater than zero.")
                return redirect('coupon_management')

        if min_purchase_amount <= 0:
                messages.error(request, "Minimum purchase amount must be greater than zero.")
                return redirect('coupon_management')

        if usage_limit <= 0:
                messages.error(request, "Usage limit must be a positive integer.")
                return redirect('coupon_management')
        
        valid_from = datetime.strptime(valid_from, '%Y-%m-%d').date()
        valid_to = datetime.strptime(valid_to, '%Y-%m-%d').date()  

        if Coupon.objects.filter(code=code).exists():
                messages.error(request, "Coupon code already exists.")
                return redirect('create_coupon')


        coupon = Coupon(
                code=code,
                discount_value=discount_value,
                min_purchase_amount=min_purchase_amount,
                valid_from=valid_from,
                valid_to=valid_to,
                usage_limit=usage_limit
            )
        coupon.save()

        messages.success(request, "Coupon created successfully.")


        
    return redirect(coupon_management)




def apply_coupon(request):
    if request.method == 'POST':
        try:
          
            data = json.loads(request.body)
            coupon_code = data.get('coupon_code')
            total_amount = Decimal(data.get('total', '0'))
            
         
            try:
                coupon = Coupon.objects.get(
                    code__iexact=coupon_code, 
                    active=True,
                    valid_from__lte=timezone.now().date(),
                    valid_to__gte=timezone.now().date()
                )
            except Coupon.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid or expired coupon code.'
                })
            
          
            if total_amount < coupon.min_purchase_amount:
                return JsonResponse({
                    'success': False,
                    'message': f'Minimum purchase amount of ₹{coupon.min_purchase_amount} required.'
                })
            
            if coupon.usage_limit <=0:
                return JsonResponse({
                    'success': False,
                    'message': 'This coupon limit exceeded'
                })
            
            
            discount_amount = min(coupon.discount_value, total_amount) 
            final_total = total_amount - discount_amount
            

            request.session['coupon_code'] = coupon_code
            request.session['discount_amount'] = str(discount_amount)
            request.session['final_total'] = str(final_total)
            
            return JsonResponse({
                'success': True,
                'message': 'Coupon applied successfully!',
                'discount_amount': str(discount_amount),
                'final_total': str(final_total),
                'original_total': str(total_amount)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Error processing coupon.',
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.'
    })


def delete_coupon(request,coupon_id):
    coupon = get_object_or_404(Coupon,id=coupon_id)
    coupon.delete()
    return redirect('coupon_management')