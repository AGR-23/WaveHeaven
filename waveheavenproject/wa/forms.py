from django import forms
from django.contrib.auth.models import User
from .models import Device  # Importamos la tabla Device del diagrama ERD

class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ["username", "email", "password"]

class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ["type", "version", "headphone_compatibility"]