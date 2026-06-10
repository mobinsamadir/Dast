from .managers import CustomUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models



import uuid
import os

def user_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return f'users/avatars/{filename}'

class CustomUser(AbstractUser):
    last_activity = models.DateTimeField(null=True, blank=True, verbose_name="آخرین فعالیت")
    consecutive_losses = models.IntegerField(default=0, verbose_name="باخت‌های متوالی")
    lifetime_coin_burn = models.IntegerField(default=0, verbose_name="کل سکه‌های مصرف شده")
    username = None # Remove standard username
    phone_number = models.CharField(max_length=15, unique=True, verbose_name="شماره موبایل")

    first_name = models.CharField(max_length=150, verbose_name="نام")
    last_name = models.CharField(max_length=150, verbose_name="نام خانوادگی")
    display_name = models.CharField(max_length=150, verbose_name="نام نمایشی")

    GENDER_CHOICES = (('مرد', 'مرد'), ('زن', 'زن'), ('ترنس', 'ترنس'))
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True, verbose_name="جنسیت")

    AGE_CHOICES = [(i, f"{i} سال") for i in range(18, 100)]
    age = models.IntegerField(choices=AGE_CHOICES, null=True, blank=True, verbose_name="سن")

    MARITAL_CHOICES = (('مجرد', 'مجرد'), ('متاهل', 'متاهل'), ('مطلقه', 'مطلقه'), ('همسر فوت شده', 'همسر فوت شده'))
    marital_status = models.CharField(max_length=20, choices=MARITAL_CHOICES, null=True, blank=True, verbose_name="وضعیت تاهل")

    children_count = models.IntegerField(default=0, verbose_name="تعداد فرزندان")
    eldest_child_age = models.IntegerField(null=True, blank=True, verbose_name="سن بزرگترین فرزند")

    height = models.FloatField(null=True, blank=True, verbose_name="قد (سانتی‌متر)")
    weight = models.FloatField(null=True, blank=True, verbose_name="وزن (کیلوگرم)")

    SKIN_COLOR_CHOICES = (
        ('سفید', 'سفید'),
        ('گندمی', 'گندمی'),
        ('سبزه روشن', 'سبزه روشن'),
        ('سبزه تیره', 'سبزه تیره'),
        ('سیاه', 'سیاه'),
    )
    skin_color = models.CharField(max_length=50, choices=SKIN_COLOR_CHOICES, null=True, blank=True, verbose_name="رنگ پوست")
    beauty = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], null=True, blank=True, verbose_name="میزان زیبایی (از ۱ تا ۵)")

    STYLE_CHOICES = (('محجبه', 'محجبه'), ('بدون حجاب', 'بدون حجاب'), ('سایر', 'سایر'))
    style = models.CharField(max_length=20, choices=STYLE_CHOICES, null=True, blank=True, verbose_name="سبک پوشش")

    health_status = models.CharField(max_length=150, null=True, blank=True, verbose_name="وضعیت سلامتی")

    INCOME_CHOICES = (
        ('ندارم', 'ندارم'),
        ('کمتر از ۱۰ میلیون تومان', 'کمتر از ۱۰ میلیون تومان'),
        ('بین ۱۰ تا ۲۰ میلیون تومان', 'بین ۱۰ تا ۲۰ میلیون تومان'),
        ('بین ۲۰ تا ۵۰ میلیون تومان', 'بین ۲۰ تا ۵۰ میلیون تومان'),
        ('بیشتر از ۵۰ میلیون تومان', 'بیشتر از ۵۰ میلیون تومان'),
    )
    income = models.CharField(max_length=100, choices=INCOME_CHOICES, null=True, blank=True, verbose_name="درآمد ماهانه")

    CAR_CHOICES = (
        ('ندارم', 'ندارم'),
        ('داخلی', 'داخلی'),
        ('خارجی', 'خارجی'),
    )
    car_status = models.CharField(max_length=100, choices=CAR_CHOICES, null=True, blank=True, verbose_name="وضعیت خودرو")

    HOUSING_CHOICES = (
        ('ندارم', 'ندارم'),
        ('اجاره‌ای', 'اجاره‌ای'),
        ('شخصی', 'شخصی'),
    )
    housing_status = models.CharField(max_length=100, choices=HOUSING_CHOICES, null=True, blank=True, verbose_name="وضعیت مسکن")

    LIFESTYLE_CHOICES = (('با خانواده', 'با خانواده'), ('مستقل', 'مستقل'))
    lifestyle = models.CharField(max_length=20, choices=LIFESTYLE_CHOICES, null=True, blank=True, verbose_name="سبک زندگی")

    province = models.CharField(max_length=100, null=True, blank=True, verbose_name="استان")
    city = models.CharField(max_length=100, null=True, blank=True, verbose_name="شهر")

    location_lat = models.FloatField(null=True, blank=True)
    location_lng = models.FloatField(null=True, blank=True)
    show_location = models.BooleanField(default=False, verbose_name="نمایش موقعیت مکانی")

    bio = models.TextField(null=True, blank=True, verbose_name="درباره من")
    spouse_expectation = models.TextField(null=True, blank=True, verbose_name="انتظارات از همسر/دوست")

    security_phrase = models.CharField(max_length=255, null=True, blank=True, verbose_name="عبارت امنیتی")

    referral_code = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name="کد معرف")
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals', verbose_name="معرف")

    SEEKING_CHOICES = (
        ('دوست', 'دوست'), ('دوستی با مزایا', 'دوستی با مزایا'), ('رابطه بدون تعهد', 'رابطه بدون تعهد'),
        ('پارتنر', 'پارتنر'), ('هم‌اتاقی', 'هم‌اتاقی'), ('همسر', 'همسر')
    )
    interested_in = models.JSONField(blank=True, null=True, verbose_name="جنسیت‌های مورد علاقه")


    seeking = models.CharField(max_length=20, choices=SEEKING_CHOICES, null=True, blank=True, verbose_name="دنبال چه هستید؟")

    profile_picture = models.ImageField(upload_to=user_directory_path, null=True, blank=True, verbose_name="عکس پروفایل")

    STATUS_CHOICES = (('فعال', 'فعال'), ('مسدود', 'مسدود'), ('تایید نشده', 'تایید نشده'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='تایید نشده', verbose_name="وضعیت حساب")
    last_spin_date = models.DateTimeField(null=True, blank=True, verbose_name="آخرین چرخش گردونه")

    is_totp_enabled = models.BooleanField(default=False, verbose_name="تایید دو مرحله‌ای فعال است؟")
    is_bot_verified = models.BooleanField(default=False, verbose_name="تایید شده توسط ربات")
    bot_verification_token = models.CharField(max_length=64, null=True, blank=True)

    objects = CustomUserManager()

    class Meta:
        indexes = [
            models.Index(fields=['gender']),

        ]

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'display_name']

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = str(uuid.uuid4())[:8].upper()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.phone_number

class WhaleUser(CustomUser):
    class Meta:
        proxy = True
        verbose_name = "کاربر ویژه (Whale)"
        verbose_name_plural = "کاربران ویژه (Whales)"
