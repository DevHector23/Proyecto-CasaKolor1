# forms.py
from .models import Sugerencia
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


#sugerencias
class SugerenciaForm(forms.ModelForm):
    class Meta:
        model = Sugerencia
        fields = ['nombre', 'correo', 'sugerencia']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa tu nombre'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa tu correo electrónico'}),
            'sugerencia': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Escribe tu sugerencia aquí'}),
        }


#login
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Obligatorio. Introduce un correo válido.")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

