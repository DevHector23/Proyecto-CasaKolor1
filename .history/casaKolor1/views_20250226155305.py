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
# Primero, define el formulario de registro

class UserRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ("username", "email", "password1", "password2")



from .forms import CustomUserCreationForm  # Importa el formulario personalizado
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse


@csrf_protect
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                request.session['login_success'] = True  # Marcar inicio de sesión exitoso
                return redirect('inicio')  # Redirigir a la página principal
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

def clear_login_success(request):
    """ Eliminar la variable de sesión después de mostrar el mensaje """
    request.session.pop('login_success', None)
    return JsonResponse({'success': True})

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


#sugerencia

from django.core.mail import send_mail
from .forms import SugerenciaForm

def enviar_sugerencia(request):
    if request.method == "POST":
        form = SugerenciaForm(request.POST)
        if form.is_valid():
            sugerencia = form.save()  # Guarda en la base de datos
            form.send_email()  # Envía el correo
            return redirect('sugerencia_exitosa')  # Redirige a la página de éxito

    else:
        form = SugerenciaForm()

    return render(request, 'sugerencias.html', {'form': form})


from django.http import JsonResponse
from .models import Pedido, DetallePedido, Producto  # Asegúrate de usar el nombre correcto de tu modelo de productos
from .forms import PedidoForm
import json
from django.utils import timezone
import uuid
from django.db import transaction
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

def finalizar_compra(request):
    if request.method == 'POST':
        try:
            # Generar un token de transacción si no existe
            transaction_token = request.POST.get('transaction_token', str(uuid.uuid4()))
            
            # Clave única para esta transacción
            cache_key = f'order_token_{transaction_token}'
            
            # Verificar si esta transacción ya fue procesada
            if cache.get(cache_key):
                # Si ya fue procesada, no hacer nada más
                return JsonResponse({'success': True, 'message': 'Pedido ya procesado'})
            
            # Marcar esta transacción como en proceso
            cache.set(cache_key, True, 30)
            
            # Manejar el archivo de factura para evitar nombres duplicados
            if 'comprobante' in request.FILES:
                original_file = request.FILES['comprobante']
                # Generar un nombre único basado en timestamp y UUID
                file_name, file_extension = os.path.splitext(original_file.name)
                unique_filename = f"{file_name}_{timezone.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}{file_extension}"
                
                # Guardar temporalmente con el nuevo nombre
                path = default_storage.save(f'comprobantes/{unique_filename}', ContentFile(original_file.read()))
                request.FILES['comprobante'].name = unique_filename
            
            # Procesar el formulario
            form = PedidoForm(request.POST, request.FILES)
            if form.is_valid():
                with transaction.atomic():
                    # Crear el pedido
                    pedido = form.save(commit=False)
                    pedido.total = float(request.POST.get('total', 0))
                    pedido.fecha = timezone.now()
                    pedido.save()
                    
                    # Procesar los productos del carrito
                    items_json = request.POST.get('items', '[]')
                    print(f"Items recibidos: {items_json}")  # Depuración
                    items = json.loads(items_json)
                    detalles_correo = []
                    
                    for item in items:
                        producto_id = item.get('id')
                        cantidad = int(item.get('cantidad', 1))
                        precio = float(item.get('precio', 0))
                        # Calcular el subtotal en el servidor para mayor seguridad
                        subtotal = precio * cantidad
                        
                        try:
                            # Usar el nombre correcto de tu modelo de productos
                            producto = Producto.objects.get(id=producto_id)
                            
                            # Crear detalle del pedido
                            DetallePedido.objects.create(
                                pedido=pedido,
                                producto=producto,
                                cantidad=cantidad,
                                precio_unitario=precio,
                                subtotal=subtotal
                            )
                            
                            # Agregar información para el correo
                            detalles_correo.append(f"Producto: {producto.nombre}, Cantidad: {cantidad}, Precio: ${precio}, Subtotal: ${subtotal}")
                        except Producto.DoesNotExist:
                            print(f"Error: Producto con ID {producto_id} no encontrado")
                            # Podrías decidir continuar o abortar aquí
                    
                    # Enviar correo de confirmación
                    asunto = "Confirmación de Pedido - Casa Kolor"
                    mensaje = f"""
Hola {pedido.nombre},

¡Gracias por tu compra en Casa Kolor!

Detalles de tu pedido:
{''.join([f'\n- {detalle}' for detalle in detalles_correo])}

Total: ${pedido.total}

Tu pedido será procesado a la brevedad.

Saludos,
El equipo de Casa Kolor
                    """
                    
                    destinatario = pedido.correo
                    # Enviar copia al administrador también
                    admin_email = settings.EMAIL_HOST_USER
                    destinatarios = [destinatario, admin_email]
                    
                    try:
                        # Usar fail_silently=False para que lanze excepciones si hay problemas
                        send_mail(asunto, mensaje, settings.EMAIL_HOST_USER, destinatarios, fail_silently=False)
                        print(f"Correo enviado a {destinatarios}")
                    except Exception as mail_error:
                        print(f"Error al enviar correo: {mail_error}")
                        # A pesar del error de correo, el pedido ya se creó, así que continuamos
                    
                    # Guardar la transacción como procesada por 30 minutos
                    cache.set(cache_key, True, 60 * 30)
                    
                    return JsonResponse({'success': True, 'message': 'Pedido creado correctamente y confirmación enviada por correo'})
            else:
                # Liberar la marca en caso de error
                cache.delete(cache_key)
                print(f"Errores en el formulario: {form.errors}")
                return JsonResponse({'success': False, 'errors': form.errors})
        
        except Exception as e:
            # Capturar cualquier excepción no manejada
            print(f"Error no manejado: {str(e)}")
            # Liberar la marca en caso de error
            if 'cache_key' in locals():
                cache.delete(cache_key)
            return JsonResponse({'success': False, 'message': f'Error al procesar el pedido: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})
# def finalizar_compra(request):
#     if request.method == 'POST':
#         form = PedidoForm(request.POST, request.FILES)
#         if form.is_valid():
#             # Crear el pedido
#             pedido = form.save(commit=False)
#             pedido.total = request.POST.get('total', 0)
#             pedido.save()
            
#             # Procesar los productos del carrito
#             items = json.loads(request.POST.get('items', '[]'))
#             detalles_correo = []
            
#             for item in items:
#                 producto_id = item.get('id')
#                 cantidad = item.get('cantidad', 1)
#                 precio = item.get('precio', 0)
#                 subtotal = item.get('subtotal', 0)
                
#                 producto = productos.objects.get(id=producto_id)
                
#                 # Crear detalle del pedido
#                 DetallePedido.objects.create(
#                     pedido=pedido,
#                     producto=producto,
#                     cantidad=cantidad,
#                     precio_unitario=precio,
#                     subtotal=subtotal
#                 )
                
#                 # Agregar información para el correo
#                 detalles_correo.append(f"Producto: {producto.nombre}, Cantidad: {cantidad}, Precio: ${precio}.")
            
#             # Enviar correo de confirmación
#             asunto = "Confirmación de Pedido - Casa Kolor"
#             mensaje = f"""
#             Hola {pedido.nombre},
            
#             ¡Gracias por tu compra en Casa Kolor!
            
#             Detalles de tu pedido:
#             {''.join([f'\n- {detalle}' for detalle in detalles_correo])}
            
#             Total: ${pedido.total}
            
#             Tu pedido será procesado a la brevedad.
            
#             Saludos,
#             El equipo de Casa Kolor
#             """
            
#             destinatario = pedido.correo
            
#             send_mail(asunto, mensaje, settings.EMAIL_HOST_USER, [destinatario])
            
#             return JsonResponse({'success': True, 'message': 'Pedido creado correctamente y confirmación enviada por correo'})
#         else:
#             return JsonResponse({'success': False, 'errors': form.errors})
    
#     return JsonResponse({'success': False, 'message': 'Método no permitido'})

from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

def restablecer(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        
        if user:
            # Generar token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Construir enlace
            reset_link = request.build_absolute_uri(
                f'/cambiar-contraseña/{uid}/{token}/'
            )
            
            # Enviar correo
            send_mail(
                'Restablecimiento de contraseña',
                f'Haz clic en el siguiente enlace para restablecer tu contraseña: {reset_link}',
                'tucorreo@gmail.com',  # Reemplaza con tu correo
                [email],
                fail_silently=False,
            )
            
            messages.success(request, "Se ha enviado un enlace a tu correo electrónico.")
            return redirect('restablecer')
        else:
            messages.error(request, "No existe un usuario con ese correo electrónico.")
            return redirect('restablecer')
    
    return render(request, 'restablecer.html')

def cambiar_contraseña(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password = request.POST.get('password')
            password2 = request.POST.get('password2')
            
            if password != password2:
                messages.error(request, "Las contraseñas no coinciden.")
                return redirect('cambiar_contraseña', uidb64=uidb64, token=token)
            
            user.set_password(password)
            user.save()
            
            return redirect('confirmacion')
        
        return render(request, 'cambiar_contraseña.html')
    else:
        return redirect('login')

def confirmacion(request):
    return render(request, 'confirmacion.html')