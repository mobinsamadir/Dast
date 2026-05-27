from django.contrib import admin
from .models import FeatureFlag

@admin.register(FeatureFlag)
class FeatureFlagAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'description']
    search_fields = ['name']
    list_filter = ['is_active']
