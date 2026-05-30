from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import CustomUser

class RegisterStep1Form(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="رمز عبور")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="تایید رمز عبور")

    class Meta:
        model = CustomUser
        fields = ('phone_number', 'password')

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "رمز عبور و تایید آن مطابقت ندارند.")
        return cleaned_data

class RegisterStep2Form(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'display_name', 'gender', 'birth_date')
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }

class RegisterStep3Form(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('marital_status', 'children_count', 'eldest_child_age')

class RegisterStep4Form(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('height', 'weight', 'skin_color', 'beauty', 'style', 'health_status')

class RegisterStep5Form(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('income', 'car_status', 'housing_status', 'lifestyle')

class RegisterStep6Form(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('province', 'city', 'location_lat', 'location_lng', 'show_location')

class RegisterStep7Form(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('bio', 'spouse_expectation', 'seeking', 'target_gender', 'security_phrase', 'referral_code')

class LoginForm(forms.Form):
    phone_number = forms.CharField(max_length=15, label="شماره موبایل")
    password = forms.CharField(widget=forms.PasswordInput, label="رمز عبور")

class PasswordResetRequestForm(forms.Form):
    phone_number = forms.CharField(max_length=15, label="شماره موبایل")

class PasswordResetConfirmForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput, label="رمز عبور جدید")
    new_password_confirm = forms.CharField(widget=forms.PasswordInput, label="تایید رمز عبور جدید")

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        new_password_confirm = cleaned_data.get('new_password_confirm')
        if new_password and new_password_confirm and new_password != new_password_confirm:
            self.add_error('new_password_confirm', "رمز عبور جدید و تایید آن مطابقت ندارند.")
        return cleaned_data
