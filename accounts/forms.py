from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import CustomUser

class TailwindModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'
            else:
                field.widget.attrs['class'] = 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border'

class RegisterStep1Form(TailwindModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="رمز عبور")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="تایید رمز عبور")

    class Meta:
        model = CustomUser
        fields = ('phone_number', 'password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget.attrs['class'] = 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border'
        self.fields['password_confirm'].widget.attrs['class'] = 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border'

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "رمز عبور و تایید آن مطابقت ندارند.")
        return cleaned_data

class RegisterStep2Form(TailwindModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'display_name', 'gender', 'age')

class RegisterStep3Form(TailwindModelForm):
    class Meta:
        model = CustomUser
        fields = ('marital_status', 'children_count', 'eldest_child_age')

class RegisterStep4Form(TailwindModelForm):
    class Meta:
        model = CustomUser
        fields = ('height', 'weight', 'skin_color', 'beauty', 'style', 'health_status')

class RegisterStep5Form(TailwindModelForm):
    class Meta:
        model = CustomUser
        fields = ('income', 'car_status', 'housing_status', 'lifestyle')

class RegisterStep6Form(TailwindModelForm):
    province = forms.CharField(required=False, label="استان")
    city = forms.CharField(required=False, label="شهر")

    class Meta:
        model = CustomUser
        fields = ('province', 'city', 'show_location')

class RegisterStep7Form(TailwindModelForm):
    class Meta:
        model = CustomUser
        fields = ('bio', 'spouse_expectation', 'seeking', 'security_phrase', 'referral_code')

class LoginForm(forms.Form):
    phone_number = forms.CharField(max_length=15, label="شماره موبایل")
    password = forms.CharField(widget=forms.PasswordInput, label="رمز عبور")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border'

class PasswordResetRequestForm(forms.Form):
    phone_number = forms.CharField(max_length=15, label="شماره موبایل")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border'


class PasswordResetConfirmForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput, label="رمز عبور جدید")
    new_password_confirm = forms.CharField(widget=forms.PasswordInput, label="تایید رمز عبور جدید")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border'

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        new_password_confirm = cleaned_data.get('new_password_confirm')
        if new_password and new_password_confirm and new_password != new_password_confirm:
            self.add_error('new_password_confirm', "رمز عبور جدید و تایید آن مطابقت ندارند.")
        return cleaned_data
