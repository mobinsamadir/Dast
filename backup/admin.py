from django.contrib import admin
from django.urls import path
from django.utils.html import format_html
from django.urls import reverse

# Dummy model just to register the app in the admin index
from django.db import models

class BackupAppConfig(models.Model):
    class Meta:
        managed = False
        verbose_name = "Backup & Restore"
        verbose_name_plural = "Backup & Restore"

@admin.register(BackupAppConfig)
class BackupAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super().get_urls()
        return urls

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        download_url = reverse('download_backup')
        restore_url = reverse('restore_backup')

        html = f'''
        <div style="margin: 20px;">
            <h2>Backup Operations</h2>
            <div style="margin-top: 10px;">
                <a href="{download_url}" class="button" style="padding: 10px 15px; background: #417690; color: white; border-radius: 4px; text-decoration: none;">Download Full Backup (DB + Media)</a>
            </div>
            <div style="margin-top: 20px;">
                <a href="{restore_url}" class="button" style="padding: 10px 15px; background: #ba2121; color: white; border-radius: 4px; text-decoration: none;">Restore Backup from ZIP</a>
            </div>
        </div>
        '''
        extra_context['cl'] = self
        extra_context['action_form'] = None
        extra_context['has_add_permission'] = False

        # In jazzmin or default django admin, we inject custom content
        response = super().changelist_view(request, extra_context=extra_context)

        # A bit hacky: if it's a TemplateResponse, we can pass our HTML to the template
        if hasattr(response, 'context_data'):
            response.context_data['custom_html'] = format_html(html)

        return response
