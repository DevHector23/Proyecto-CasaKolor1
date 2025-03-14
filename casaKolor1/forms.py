# forms.py
from .models import Sugerencia
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django import forms
from django.contrib.auth.models import User

# class UserRegistrationForm(UserCreationForm):
#     email = forms.EmailField(required=True)
    
#     class Meta:
#         model = User
#         fields = ("username", "email", "password1", "password2")

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Correo electrónico'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Nombre de usuario'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Repetir contraseña'}))
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


#sugerencias
# class SugerenciaForm(forms.ModelForm):
#     class Meta:
#          model = Sugerencia
#          fields = ['nombre', 'correo', 'sugerencia']
#          widgets = {
#              'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa tu nombre'}),
#              'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa tu correo electrónico'}),
#              'sugerencia': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Escribe tu sugerencia aquí'}),
#          }


#login
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Correo electrónico'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Nombre de usuario'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Repetir contraseña'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Nombre de usuario'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'}))




from django import forms
from django.core.mail import send_mail
from django.conf import settings
from .models import Sugerencia  # Importa el modelo

class SugerenciaForm(forms.ModelForm):
    class Meta:
        model = Sugerencia
        fields = ['nombre', 'correo', 'sugerencia']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa tu nombre'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa tu correo electrónico'}),
            'sugerencia': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Escribe tu sugerencia aquí'}),
        }

    def send_email(self):
        """Método para enviar el correo con la sugerencia"""
        asunto = "Nueva Sugerencia Recibida"
        mensaje = (
            f"Has recibido una nueva sugerencia de {self.cleaned_data['nombre']} ({self.cleaned_data['correo']}):\n\n"
            f"{self.cleaned_data['sugerencia']}"
        )
        destinatario = "hector3208609853@gmail.com"

        send_mail(asunto, mensaje, settings.EMAIL_HOST_USER, [destinatario])

from django import forms
from .models import Pedido

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['nombre', 'correo', 'telefono', 'comprobante']
        
    def clean_comprobante(self):
        comprobante = self.cleaned_data.get('comprobante')
        if comprobante:
            ext = comprobante.name.split('.')[-1].lower()
            valid_extensions = ['jpg', 'jpeg', 'png', 'pdf']
            
            if ext not in valid_extensions:
                raise forms.ValidationError('El comprobante debe ser una imagen o PDF.')
                
            if comprobante.size > 5 * 1024 * 1024:
                raise forms.ValidationError('El tamaño máximo permitido es 5MB.')
                
        return comprobante