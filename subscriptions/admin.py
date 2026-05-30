from django.contrib import admin
from .models import Plan, Subscription, Wallet, CoinTransaction, GiftPacket, UserGift, CoinPackage

class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration_days', 'price')

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'start_date', 'end_date', 'is_active')

class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'coin_balance')

class CoinTransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'amount', 'before_balance', 'after_balance', 'transaction_type', 'created_at')

class GiftPacketAdmin(admin.ModelAdmin):
    list_display = ('name', 'coins', 'price', 'admin_commission_percent')

class UserGiftAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'gift_packet', 'sent_at')

class CoinPackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'coins', 'price')

admin.site.register(Plan, PlanAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Wallet, WalletAdmin)
admin.site.register(CoinTransaction, CoinTransactionAdmin)
admin.site.register(GiftPacket, GiftPacketAdmin)
admin.site.register(UserGift, UserGiftAdmin)
admin.site.register(CoinPackage, CoinPackageAdmin)
