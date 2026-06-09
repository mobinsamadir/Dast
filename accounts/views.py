from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from formtools.wizard.views import SessionWizardView
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from .forms import (
    RegisterStep1Form, RegisterStep2Form, RegisterStep3Form, RegisterStep4Form,
    RegisterStep5Form, RegisterStep6Form, RegisterStep7Form, LoginForm,
    PasswordResetRequestForm, PasswordResetConfirmForm
)
from .models import CustomUser
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from .utils import get_haversine_expression, similarity_score
import os

FORMS = [
    ("step1", RegisterStep1Form),
    ("step2", RegisterStep2Form),
    ("step3", RegisterStep3Form),
    ("step4", RegisterStep4Form),
    ("step5", RegisterStep5Form),
    ("step6", RegisterStep6Form),
    ("step7", RegisterStep7Form),
]

TEMPLATES = {
    "step1": "accounts/wizard/step1.html",
    "step2": "accounts/wizard/step2.html",
    "step3": "accounts/wizard/step3.html",
    "step4": "accounts/wizard/step4.html",
    "step5": "accounts/wizard/step5.html",
    "step6": "accounts/wizard/step6.html",
    "step7": "accounts/wizard/step7.html",
}

@method_decorator(ratelimit(key='ip', rate='10/h', method=['POST'], block=True), name='dispatch')
class RegistrationWizard(SessionWizardView):
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'temp'))

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        form_data = {}
        for form in form_list:
            form_data.update(form.cleaned_data)

        password = form_data.pop('password')
        form_data.pop('password_confirm', None)

        referral_code = form_data.get('referral_code')
        referred_by = None
        if referral_code:
            try:
                referred_by = CustomUser.objects.get(referral_code=referral_code)
                form_data['referred_by'] = referred_by
            except CustomUser.DoesNotExist:
                pass

        user = CustomUser.objects.create_user(**form_data, password=password)

        if referred_by:
            pass

        login(self.request, user)
        messages.success(self.request, 'ثبت‌نام با موفقیت انجام شد.')
        return redirect('landing')

def register_view(request):
    return redirect('register_wizard')

@ratelimit(key='ip', rate='5/m', method=['POST'], block=True)
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data.get('phone_number')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=phone, password=password)
            if user is not None:
                if user.status == 'Blocked':
                    messages.error(request, 'حساب کاربری شما مسدود شده است.')
                    return render(request, 'accounts/login.html', {'form': form})
                login(request, user)
                return redirect('landing')
            else:
                messages.error(request, 'شماره موبایل یا رمز عبور اشتباه است.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('landing')

@ratelimit(key='ip', rate='3/h', method=['POST'], block=True)
def password_reset_request_view(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data.get('phone_number')
            try:
                user = CustomUser.objects.get(phone_number=phone)
                request.session['reset_phone'] = phone
                return redirect('password_reset_confirm')
            except CustomUser.DoesNotExist:
                messages.error(request, 'کاربری با این شماره موبایل یافت نشد.')
    else:
        form = PasswordResetRequestForm()
    return render(request, 'accounts/password_reset_request.html', {'form': form})

@ratelimit(key='ip', rate='5/h', method=['POST'], block=True)
def password_reset_confirm_view(request):
    phone = request.session.get('reset_phone')
    if not phone:
        return redirect('password_reset_request')

    if request.method == 'POST':
        form = PasswordResetConfirmForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data.get('new_password')
            user = CustomUser.objects.get(phone_number=phone)
            user.set_password(new_password)
            user.save()
            del request.session['reset_phone']
            messages.success(request, 'رمز عبور با موفقیت تغییر یافت. لطفاً وارد شوید.')
            return redirect('login')
    else:
        form = PasswordResetConfirmForm()
    return render(request, 'accounts/password_reset_confirm.html', {'form': form})

@login_required
def profile_detail(request, user_id):
    target_user = get_object_or_404(CustomUser, id=user_id)
    if target_user.status == 'Blocked':
        messages.error(request, 'این کاربر مسدود شده است.')
        return redirect('landing')

    similar_users = CustomUser.objects.annotate(
        similarity=similarity_score(target_user)
    ).exclude(id=user_id).exclude(status='Blocked').order_by('-similarity')[:4]

    return render(request, 'accounts/profile.html', {'target_user': target_user, 'similar_users': similar_users})

@login_required
def search_users(request):
    query = request.GET.get('q', '')
    gender_filter = request.GET.getlist('gender')

    is_vip = request.user.subscriptions.filter(is_active=True).exists()

    # Dark Pattern / Paywall: Block TS search or multi-gender search for free users
    if not is_vip:
        if 'ترنس' in gender_filter or len(gender_filter) > 1:
            messages.error(request, '🔒 جستجوی پیشرفته (چند جنسیتی یا ترنس) نیازمند حساب ویژه است.')
            return redirect('plans') # Redirect to VIP purchase page

    users = CustomUser.objects.exclude(status='Blocked')
    if query:
        users = users.filter(display_name__icontains=query)
    if gender_filter:
        users = users.filter(gender__in=gender_filter)

    users = users[:20]
    return render(request, 'accounts/search.html', {'users': users, 'is_vip': is_vip})

@login_required
def nearby_users(request):
    if not request.user.show_location or request.user.location_lat is None or request.user.location_lng is None:
        messages.warning(request, 'برای مشاهده کاربران نزدیک، لطفا موقعیت مکانی خود را در پروفایل ثبت و فعال کنید.')
        return redirect('landing')

    users = CustomUser.objects.filter(
        show_location=True,
        location_lat__isnull=False,
        location_lng__isnull=False
    ).exclude(status='Blocked').exclude(id=request.user.id)

    users = users.annotate(
        distance=get_haversine_expression(request.user.location_lat, request.user.location_lng)
    ).order_by('distance')[:20]

    return render(request, 'accounts/nearby.html', {'users': users})

@login_required
def my_profile(request):
    if request.method == 'POST':
        user = request.user

        def get_val(key, existing):
            val = request.POST.get(key)
            return val if val else existing

        user.display_name = get_val('display_name', user.display_name)
        user.bio = get_val('bio', user.bio)
        user.city = get_val('city', user.city)
        user.province = get_val('province', user.province)
        user.age = get_val('age', user.age)

        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']

        user.save()
        messages.success(request, 'پروفایل شما با موفقیت بروزرسانی شد.')
        return redirect('my_profile')

    return render(request, 'accounts/my_profile.html', {'user': request.user})
