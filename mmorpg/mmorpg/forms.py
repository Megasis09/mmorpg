from django.contrib.auth.forms import UserCreationForm
from .models import User, Newsletter

from django import forms
from .models import Ad

class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = ('title', 'text')

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, help_text='Обязательное поле.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ('subject', 'message')