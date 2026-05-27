from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from .models import CustomUser
from django.contrib import messages

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'ثبت‌نام با موفقیت انجام شد.')
            return redirect('landing')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    # Dummy login view for preview
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        user = authenticate(request, username=phone, password=password)
        if user is not None:
            login(request, user)
            return redirect('landing')
        else:
            messages.error(request, 'شماره موبایل یا رمز عبور اشتباه است.')
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('landing')

@login_required
def profile_detail(request, user_id):
    target_user = get_object_or_404(CustomUser, id=user_id)
    similar_users = CustomUser.objects.filter(city=target_user.city, seeking=target_user.seeking).exclude(id=user_id)[:4]
    return render(request, 'accounts/profile.html', {'target_user': target_user, 'similar_users': similar_users})

@login_required
def search_users(request):
    query = request.GET.get('q', '')
    users = CustomUser.objects.filter(display_name__icontains=query) if query else CustomUser.objects.all()[:20]
    return render(request, 'accounts/search.html', {'users': users})

@login_required
def nearby_users(request):
    # Placeholder for geospatial query
    users = CustomUser.objects.filter(show_location=True).exclude(id=request.user.id)[:20]
    return render(request, 'accounts/nearby.html', {'users': users})
