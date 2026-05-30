from django.contrib import admin
from .models import PaymentTransaction
from django.utils import timezone
from datetime import timedelta
from subscriptions.models import Plan, Subscription, Wallet, CoinPackage

def approve_payments(modeladmin, request, queryset):
    for payment in queryset.filter(status='Pending'):
        payment.status = 'Approved'
        payment.approved_at = timezone.now()
        payment.save()

        # Check what the payment was for
        if payment.target_item and payment.target_item.startswith('plan_'):
            try:
                plan_id = int(payment.target_item.split('_')[1])
                plan = Plan.objects.get(id=plan_id)
                Subscription.objects.create(
                    user=payment.user,
                    plan=plan,
                    end_date=timezone.now() + timedelta(days=plan.duration_days)
                )
            except Plan.DoesNotExist:
                pass
        elif payment.target_item and payment.target_item.startswith('coins_'):
            try:
                package_id = int(payment.target_item.split('_')[1])
                package = CoinPackage.objects.get(id=package_id)
                wallet, _ = Wallet.objects.get_or_create(user=payment.user)
                from subscriptions.utils import add_coins
                add_coins(payment.user, package.coins, 'Purchase', f"Purchased {package.name}")
            except CoinPackage.DoesNotExist:
                pass

approve_payments.short_description = "Approve selected payments and grant items"

def reject_payments(modeladmin, request, queryset):
    queryset.update(status='Rejected')
reject_payments.short_description = "Reject selected payments"

class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'status', 'target_item', 'created_at', 'approved_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__phone_number', 'tracking_code')
    actions = [approve_payments, reject_payments]

admin.site.register(PaymentTransaction, PaymentTransactionAdmin)
