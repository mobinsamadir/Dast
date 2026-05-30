from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Wallet, Plan, CoinPackage, GiftPacket, UserGift
from payments.models import PaymentTransaction
from django.contrib import messages
from .utils import deduct_coins, add_coins
from accounts.models import CustomUser

@login_required
def wallet_view(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    transactions = wallet.transactions.all().order_by('-created_at')[:20]
    return render(request, 'subscriptions/wallet.html', {'wallet': wallet, 'transactions': transactions})

@login_required
def buy_coins_view(request):
    packages = CoinPackage.objects.all().order_by('price')
    return render(request, 'subscriptions/buy_coins.html', {'packages': packages})

@login_required
def plans_view(request):
    plans = Plan.objects.all().order_by('price')
    return render(request, 'subscriptions/plans.html', {'plans': plans})

@login_required
def upload_receipt_view(request):
    target_item = request.GET.get('target', '')
    amount = request.GET.get('amount', 0)

    if request.method == 'POST':
        receipt_image = request.FILES.get('receipt_image')
        tracking_code = request.POST.get('tracking_code')
        amount = request.POST.get('amount')
        target_item = request.POST.get('target_item')

        if receipt_image and amount:
            PaymentTransaction.objects.create(
                user=request.user,
                amount=amount,
                receipt_image=receipt_image,
                tracking_code=tracking_code,
                target_item=target_item
            )
            messages.success(request, 'رسید شما با موفقیت ثبت شد و پس از تایید مدیریت اعمال خواهد شد.')
            return redirect('landing')
        else:
            messages.error(request, 'لطفا رسید و مبلغ را وارد کنید.')

    return render(request, 'subscriptions/upload_receipt.html', {'target_item': target_item, 'amount': amount})

@login_required
def gift_catalog_view(request):
    gifts = GiftPacket.objects.all().order_by('price')
    return render(request, 'subscriptions/gift_catalog.html', {'gifts': gifts})

@login_required
def send_gift_view(request, receiver_id):
    receiver = get_object_or_404(CustomUser, id=receiver_id)
    if request.method == 'POST':
        gift_id = request.POST.get('gift_id')
        gift = get_object_or_404(GiftPacket, id=gift_id)

        # Deduct price from sender
        if deduct_coins(request.user, gift.price, 'Gift', f"Sent gift '{gift.name}' to {receiver.phone_number}"):
            # Commission calculation
            received_coins = int(gift.coins * (1 - gift.admin_commission_percent / 100.0))

            # Add to receiver
            add_coins(receiver, received_coins, 'Gift', f"Received gift '{gift.name}' from {request.user.phone_number}")

            # Log the gift
            UserGift.objects.create(sender=request.user, receiver=receiver, gift_packet=gift)
            messages.success(request, 'هدیه با موفقیت ارسال شد.')
            return redirect('profile_detail', user_id=receiver.id)
        else:
            messages.error(request, 'موجودی سکه شما کافی نیست.')
            return redirect('buy_coins')

    gifts = GiftPacket.objects.all().order_by('price')
    return render(request, 'subscriptions/send_gift.html', {'receiver': receiver, 'gifts': gifts})
