from django.shortcuts import render
from django.contrib.auth import get_user_model

User = get_user_model()

def landing_page(request):
    # Fetch recent users with profile pictures
    new_users = User.objects.filter(profile_picture__isnull=False, status='Active').order_by('-date_joined')[:12]
    return render(request, 'landing.html', {'new_users': new_users})
