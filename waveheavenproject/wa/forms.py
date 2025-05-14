from django import forms
from django.contrib.auth.models import User
from .models import Device
from datetime import date

class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    birthday = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True,
        label="Date of Birth"
    )

    class Meta:
        model = User
        fields = ["username", "email", "password", "birthday"]

    def clean_birthday(self):
        birthday = self.cleaned_data.get("birthday")
        today = date.today()

        if birthday:
            age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
            if age < 13:
                raise forms.ValidationError("You must be at least 13 years old to register.")
        
        return birthday


class DeviceForm(forms.ModelForm):
    OS_CHOICES = [
        ("Android", "Android"),
        ("iOS", "iOS"),
        ("Other", "Other"),
    ]
    
    type = forms.ChoiceField(
        choices=OS_CHOICES,
        widget=forms.Select,
        label="Operating System"
    )

    class Meta:
        model = Device
        fields = ["type"]