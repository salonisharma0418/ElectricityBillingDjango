from django import forms
from .models import ImageUpload
from django.contrib.auth.forms import  UserCreationForm, AuthenticationForm
from .models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2']

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email')


class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = ImageUpload
        fields = ['image']


