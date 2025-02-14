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
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Loguear al usuario automáticamente después del registro
            login(request, user)
            return redirect('inicio')  # Redirige a la página principal
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})



def login_view(request):
     if request.method == 'POST':
         form = AuthenticationForm(request, data=request.POST)
         if form.is_valid():
             username = form.cleaned_data.get('username')
             password = form.cleaned_data.get('password')
             user = authenticate(request, username=username, password=password)
             if user is not None:
                 login(request, user)
                 return redirect('inicio')  # Redirige a la página principal
             else:
                 form.add_error(None, 'Usuario o contraseña incorrectos')
     else:
         form = AuthenticationForm()

     return render(request, 'login.html', {'form': form})



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
