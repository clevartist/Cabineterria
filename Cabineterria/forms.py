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
        help_texts = {
            'username': None,
        }

class SignupForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']
        help_texts = {
            'username': None,
        }
    
    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Username already exists.")
        
        return username