from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Wallet

@login_required
def wallet_view(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    transactions = wallet.transactions.all().order_by('-created_at')[:10]
    return render(request, 'subscriptions/wallet.html', {'wallet': wallet, 'transactions': transactions})
