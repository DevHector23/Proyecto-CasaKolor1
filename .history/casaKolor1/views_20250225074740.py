from .forms import UserRegistrationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from .models import productos
from django.conf import settings





def home(request):
    return render(request, 'home.html')


def inicio(request):
    return render(request, 'inicio.html')


def productos_view(request):
    productos_list = productos.objects.all()
    return render(request, 'productos.html', {
        'productos': productos_list 
        
     })

def sugerencias(request):
    return render(request, 'sugerencias.html')

def carrito(request):
    return render(request, 'carrito.html')



#registro de usuario
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.shortcuts import redirect, render

# Primero, define el formulario de registro
class UserRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ("username", "email", "password1", "password2")


from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import CustomUserCreationForm  # Importa el formulario personalizado
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.csrf import csrf_protect

@csrf_protect
# def mi_vista(request):
#     if request.method == "POST":
#         # Procesar datos
#         pass
#     return render(request, "mi_template.html")
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('inicio')  # Cambia 'inicio' por tu página principal
    else:
        form = AuthenticationForm()

    register_form = CustomUserCreationForm()  # Usar el nuevo formulario con email
    return render(request, 'login.html', {
        'form': form,
        'register_form': register_form
    })

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()  # Guarda el usuario, pero NO inicia sesión automáticamente
            return redirect('login')  # Redirige al login en lugar de iniciar sesión
    else:
        form = CustomUserCreationForm()

    return render(request, 'login.html', {'register_form': form}) 



def logout_view(request):
    logout(request)
    return redirect('inicio')  # Redirige a la página principal




def lista_pinturas(request):
    lista_productos = productos.objects.filter(categoria='pinturas')
    return render(request, 'pinturas.html', {'productos': lista_productos})

def lista_herramientas(request):
    lista_herramientas =productos.objects.filter(categoria='herramientas')
    return render(request, 'herramientas.html', {'productos': lista_herramientas})



def mision(request):
    context = {
         'MEDIA_URL': settings.MEDIA_URL
      }
    return render(request, 'mision.html', context)


#sugerencias
from .forms import SugerenciaForm

def sugerencia_view(request):
     if request.method == 'POST':
         form = SugerenciaForm(request.POST)
         if form.is_valid():
             form.save()
             return redirect('sugerencia_exitosa')  # Redirige a una página de éxito
     else:
         form = SugerenciaForm()
    
     return render(request, 'sugerencias.html', {'form': form})


    def sugerencia_exitosa(request):
    return render(request, 'sugerencia_exitosa.html')


#buscar
from django.db.models import Q


def buscar(request):
    query = request.GET.get('query', '')
    resultados = productos.objects.filter(
        Q(nombre__icontains=query) | 
        Q(descripcion__icontains=query)
    )
    return render(request, 'buscar.html', {
        'resultados': resultados, 
        'query': query
    })


#factura


from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.conf import settings  # Importar settings correctamente
from .forms import SugerenciaForm  

def enviar_sugerencia(request):
    if request.method == "POST":
        form = SugerenciaForm(request.POST)
        if form.is_valid():
            sugerencia = form.cleaned_data['sugerencia']
            nombre = form.cleaned_data.get('nombre', 'Anónimo')
            email = form.cleaned_data.get('email', 'No proporcionado')

            # Enviar correo
            asunto = "Nueva Sugerencia Recibida"
            mensaje = f"Has recibido una nueva sugerencia de {nombre} ({email}):\n\n{sugerencia}"
            destinatario = "hector3208609853@gmail.com"

            try:
                send_mail(asunto, mensaje, settings.EMAIL_HOST_USER, [destinatario])
                return redirect('sugerencia_exitosa')  # Redirige si el correo se envía correctamente
            except Exception as e:
                print(f"Error al enviar el correo: {e}")  # Muestra el error en la consola
                form.add_error(None, "Hubo un problema al enviar la sugerencia. Inténtalo más tarde.")

    else:
        form = SugerenciaForm()

    return render(request, 'sugerencias.html', {'form': form})

