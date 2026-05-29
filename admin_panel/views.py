from django.http import JsonResponse
import psutil
from django.db import connection


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
