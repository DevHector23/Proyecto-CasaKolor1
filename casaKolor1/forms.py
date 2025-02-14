# forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Sugerencia


class UserRegistrationForm(forms.ModelForm):
      password = forms.CharField(widget=forms.PasswordInput)

      class Meta:
        model = User
        fields = ['username', 'email', 'password']


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


#factura
