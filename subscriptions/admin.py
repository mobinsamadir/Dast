from django.contrib import admin
from .models import Plan, Subscription, Wallet, CoinTransaction, GiftPacket, UserGift

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'duration_days', 'price']

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active']
    search_fields = ['user__phone_number']

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'coin_balance']
    search_fields = ['user__phone_number']

@admin.register(CoinTransaction)
class CoinTransactionAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'amount', 'transaction_type', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['wallet__user__phone_number']

@admin.register(GiftPacket)
class GiftPacketAdmin(admin.ModelAdmin):
    list_display = ['name', 'coins', 'price', 'admin_commission_percent']

@admin.register(UserGift)
class UserGiftAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'gift_packet', 'sent_at']
    search_fields = ['sender__phone_number', 'receiver__phone_number']
