from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Wallet, WalletTransaction

@login_required
def wallet_history(request):
    try:
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        transactions = WalletTransaction.objects.filter(wallet=wallet).order_by('-created_at')
        
        context = {
            'wallet': wallet,
            'transactions': transactions,
        }
        return render(request, 'wallet_history.html', context)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Error fetching wallet history for user {request.user.id}: {str(e)}", exc_info=True)
        return render(request, 'wallet_history.html', {'error': 'Could not load wallet history.'})
