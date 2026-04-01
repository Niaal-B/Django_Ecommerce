from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Wallet, WalletTransaction

@login_required
def wallet_history(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    transactions = WalletTransaction.objects.filter(wallet=wallet).order_by('-created_at')
    
    context = {
        'wallet': wallet,
        'transactions': transactions,
    }
    return render(request, 'wallet_history.html', context)
