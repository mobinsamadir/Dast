from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
import psutil
from django.db import connection

# For Analytics
from django.db.models import Sum, Count, Q, F
from django.db.models.functions import TruncDay, TruncHour, TruncWeek
from django.utils import timezone
from datetime import timedelta
import json

from accounts.models import CustomUser
from games.models import GameRoom

def health_check(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"error": "Authentication required", "status": 401},
            status=401
        )
    if not request.user.is_staff:
        return JsonResponse(
            {"error": "Staff access required", "status": 403},
            status=403
        )
    try:
        connection.ensure_connection()
        db_ok = True
    except Exception:
        db_ok = False

    ram_usage = psutil.virtual_memory().percent
    cpu_usage = psutil.cpu_percent(interval=0.1)
    disk_usage = psutil.disk_usage('/').percent

    return JsonResponse({
        'status': 'ok' if db_ok else 'error',
        'database': 'ok' if db_ok else 'error',
        'ram_percent': ram_usage,
        'cpu_percent': cpu_usage,
        'disk_percent': disk_usage
    })

def can_view_growth_dashboard(user):
    return user.is_active and user.is_staff and not user.groups.filter(name='Staff_No_Growth').exists()

@staff_member_required
@user_passes_test(can_view_growth_dashboard, login_url='/admin/')
def growth_dashboard_view(request):
    now = timezone.now()
    seven_days_ago = now - timedelta(days=7)
    
    # 1. P&L (House Edge accumulation)
    games_qs = GameRoom.objects.filter(status='FINISHED')
    
    # Simple House Edge calculation in Python since it depends on capacity and reward pool
    # A more robust DB approach requires annotations, but this suffices for phase 6 overview.
    # House Edge = (entry_fee * capacity) - reward_pool
    # Let's aggregate it via DB:
    pl_data = games_qs.filter(created_at__gte=seven_days_ago).annotate(
        day=TruncDay('created_at')
    ).values('day').annotate(
        total_edge=Sum(F('entry_fee') * F('capacity') - F('reward_pool'))
    ).order_by('day')
    
    pl_labels = [entry['day'].strftime('%Y-%m-%d') for entry in pl_data]
    pl_values = [entry['total_edge'] for entry in pl_data]
    
    # 2. Conversion Rate
    total_users = CustomUser.objects.exclude(status='Blocked').count()
    vip_users = CustomUser.objects.filter(subscriptions__is_active=True).distinct().count()
    conversion_rate = (vip_users / total_users * 100) if total_users > 0 else 0
    
    # 3. Game Velocity (Games per hour in last 24h)
    velocity_data = games_qs.filter(created_at__gte=now - timedelta(days=1)).annotate(
        hour=TruncHour('created_at')
    ).values('hour').annotate(
        count=Count('id')
    ).order_by('hour')
    
    velocity_labels = [entry['hour'].strftime('%H:00') for entry in velocity_data]
    velocity_values = [entry['count'] for entry in velocity_data]
    
    context = {
        'pl_labels': json.dumps(pl_labels),
        'pl_values': json.dumps(pl_values),
        'conversion_rate': round(conversion_rate, 2),
        'vip_users': vip_users,
        'total_users': total_users,
        'velocity_labels': json.dumps(velocity_labels),
        'velocity_values': json.dumps(velocity_values),
        'title': 'داشبورد هوش رشد (Growth Intelligence)',
    }
    
    return render(request, 'admin/growth_dashboard.html', context)
