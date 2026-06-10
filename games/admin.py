from django.contrib import admin
from .models import GameRoom, TruthDareQuestion, Gift, LootBox, LootBoxItem, BetHistory

@admin.register(GameRoom)
class GameRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'game_type', 'status', 'created_at')
    list_filter = ('game_type', 'status')
    search_fields = ('id',)

@admin.register(TruthDareQuestion)
class TruthDareQuestionAdmin(admin.ModelAdmin):
    list_display = ('q_type', 'text')
    list_filter = ('q_type',)

@admin.register(Gift)
class GiftAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_coins')

class LootBoxItemInline(admin.TabularInline):
    model = LootBoxItem
    extra = 1

@admin.register(LootBox)
class LootBoxAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_coins', 'is_premium')
    inlines = [LootBoxItemInline]

@admin.register(BetHistory)
class BetHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'amount', 'won', 'payout', 'created_at')
    list_filter = ('won',)
    search_fields = ('user__phone_number',)
