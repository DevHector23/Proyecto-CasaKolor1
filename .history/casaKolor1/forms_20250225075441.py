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
from django import forms
from django.core.mail import send_mail
from .models import Sugerencia

class SugerenciaForm(forms.ModelForm): 
    class Meta:
        model = Sugerencia
        fields = ['nombre', 'correo', 'sugerencia']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa tu nombre'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa tu correo electrónico'}),
            'sugerencia': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Escribe tu sugerencia aquí'}),
        }

    # Método para enviar correo después de validar el formulario
    def send_email(self):
        asunto = "Nueva sugerencia recibida"
        mensaje = f"Nombre: {self.cleaned_data['nombre']}\n"
        mensaje += f"Correo: {self.cleaned_data['correo']}\n"
        mensaje += f"Sugerencia:\n{self.cleaned_data['sugerencia']}"
        
        send_mail(
            asunto,
            mensaje,
            'tu_correo@example.com',  # Remitente (ajústalo con tu correo)
            ['destinatario@example.com'],  # Correo destinatario
            fail_silently=False,  # Lanza error si no se envía correctamente
        )



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




# from django import forms

# class SugerenciaForm(forms.Form):
#     nombre = forms.CharField(max_length=100, required=False, label="Nombre")
#     email = forms.EmailField(required=False, label="Correo Electrónico")
#     sugerencia = forms.CharField(widget=forms.Textarea, label="Sugerencia")
