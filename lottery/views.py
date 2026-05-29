from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from subscriptions.decorators import subscription_required
from .models import Lottery, Ticket
from django.contrib import messages
from subscriptions.utils import deduct_coins

@login_required
def lottery_list_view(request):
    active_lotteries = Lottery.objects.filter(is_active=True).order_by('draw_date')
    return render(request, 'lottery/list.html', {'lotteries': active_lotteries})

@login_required
def lottery_detail_view(request, lottery_id):
    lottery = get_object_or_404(Lottery, id=lottery_id)
    user_tickets = Ticket.objects.filter(lottery=lottery, user=request.user)
    return render(request, 'lottery/detail.html', {'lottery': lottery, 'user_tickets': user_tickets})

@login_required
@subscription_required
def buy_ticket_view(request, lottery_id):
    lottery = get_object_or_404(Lottery, id=lottery_id, is_active=True)

    if request.method == 'POST':
        user_tickets_count = Ticket.objects.filter(lottery=lottery, user=request.user).count()
        if user_tickets_count >= lottery.max_tickets_per_user:
            messages.error(request, f'شما به حداکثر تعداد مجاز بلیت برای این قرعه‌کشی ({lottery.max_tickets_per_user} عدد) رسیده‌اید.')
            return redirect('lottery_detail', lottery_id=lottery.id)

        if deduct_coins(request.user, lottery.ticket_price, 'Purchase', f'خرید بلیت قرعه‌کشی {lottery.title}'):
            ticket = Ticket.objects.create(lottery=lottery, user=request.user)
            messages.success(request, f'بلیت شما با شماره {ticket.ticket_number} با موفقیت خریداری شد.')
        else:
            messages.error(request, 'موجودی سکه شما کافی نیست.')

    return redirect('lottery_detail', lottery_id=lottery.id)

@login_required
def my_tickets_view(request):
    tickets = Ticket.objects.filter(user=request.user).order_by('-purchase_date')
    return render(request, 'lottery/my_tickets.html', {'tickets': tickets})

@login_required
def winners_view(request):
    past_lotteries = Lottery.objects.filter(is_active=False, winner__isnull=False).order_by('-draw_date')
    return render(request, 'lottery/winners.html', {'lotteries': past_lotteries})
