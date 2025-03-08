from django import forms
from .models import CabinetModel
from django.contrib.auth.models import User

class CabinetForm(forms.ModelForm):
    class Meta:
        model = CabinetModel
        fields = ['name', 'description']

class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']

class SignupForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']