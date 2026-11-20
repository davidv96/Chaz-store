from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "password1", "password2", "phone", "address")
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "phone", "address")
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
        }
