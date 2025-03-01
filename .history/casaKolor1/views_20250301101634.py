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


from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token

@ensure_csrf_cookie  # Esta decorador asegura que se envíe una cookie CSRF
def login_view(request):
    # Forzar la generación del token CSRF
    get_token(request)
    
    # Preparar ambos formularios para que estén disponibles siempre
    login_form = AuthenticationForm()
    register_form = CustomUserCreationForm()
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                request.session['login_success'] = True
                return redirect('inicio')
        # Si hay errores, simplemente continuamos para mostrar el formulario nuevamente
    
    # Siempre pasamos ambos formularios al template
    return render(request, 'login.html', {
        'form': login_form,
        'register_form': register_form
    })

# También aplica el decorador a la vista de registro
@ensure_csrf_cookie
def register_view(request):
    # Forzar la generación del token CSRF
    get_token(request)
    
    # Preparar ambos formularios
    login_form = AuthenticationForm()
    register_form = CustomUserCreationForm()
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        else:
            register_form = form
    
    return render(request, 'login.html', {
        'form': login_form,
        'register_form': register_form,
        'mode': 'register'
    }) 
from django.shortcuts import redirect

def clear_login_success(request):
    # Elimina cualquier dato de sesión relacionado con el login exitoso
    if 'login_success' in request.session:
        del request.session['login_success']
    return redirect('inicio')  # Cambia esto por la URL a donde quieres redirigir

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
from .models import Pedido, DetallePedido
from .forms import PedidoForm
import json
from django.utils import timezone
import uuid
from django.db import transaction
from django.core.cache import cache

def finalizar_compra(request):
    if request.method == 'POST':
        # Extraer el token de la transacción
        transaction_token = request.POST.get('transaction_token')
        
        # Clave única para esta transacción
        cache_key = f'order_token_{transaction_token}'
        
        # Verificar si esta transacción ya fue procesada
        if cache.get(cache_key):
            # Si ya fue procesada, no hacer nada más
            return JsonResponse({'success': True, 'message': 'Pedido ya procesado'})
        
        # Marcar esta transacción como en proceso por 30 segundos
        # (suficiente para que termine el procesamiento)
        cache.set(cache_key, True, 30)
        
        form = PedidoForm(request.POST, request.FILES)
        if form.is_valid():
            # Crear el pedido
            pedido = form.save(commit=False)
            pedido.total = request.POST.get('total', 0)
            
            # Guardar la imagen de la factura si fue proporcionada
            if 'factura' in request.FILES:
                pedido.factura = request.FILES['factura']
                
            pedido.save()
            
            # Procesar los productos del carrito
            items = json.loads(request.POST.get('items', '[]'))
            detalles_correo = []
            
            for item in items:
                producto_id = item.get('id')
                cantidad = item.get('cantidad', 1)
                precio = item.get('precio', 0)
                subtotal = item.get('subtotal', 0)
                
                producto = productos.objects.get(id=producto_id)
                
                # Crear detalle del pedido
                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=precio,
                    subtotal=subtotal
                )
                
                # Agregar información para el correo
                detalles_correo.append(f"Producto: {producto.nombre}, Cantidad: {cantidad}, Precio: ${precio}.")
            
            # Preparar el correo
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
            
            # Preparar el email
            from django.core.mail import EmailMultiAlternatives
            from django.template.loader import render_to_string
            from django.utils.html import strip_tags
            
            # Crear una versión HTML del correo para poder mostrar la imagen
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #f8f9fa; padding: 10px; text-align: center; }}
                    .content {{ padding: 20px 0; }}
                    .footer {{ font-size: 12px; color: #6c757d; text-align: center; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>Confirmación de Pedido - Casa Kolor</h2>
                    </div>
                    <div class="content">
                        <p>Hola {pedido.nombre},</p>
                        <p>¡Gracias por tu compra en Casa Kolor!</p>
                        <h3>Detalles de tu pedido:</h3>
                        <ul>
                            {''.join([f'<li>{detalle}</li>' for detalle in detalles_correo])}
                        </ul>
                        <p><strong>Total:</strong> ${pedido.total}</p>
                        
                        <h3>Comprobante de pago:</h3>
                        <p>Se ha recibido tu comprobante de pago.</p>
                        
                        <p>Tu pedido será procesado a la brevedad.</p>
                        <p>Saludos,<br>El equipo de Casa Kolor</p>
                    </div>
                    <div class="footer">
                        <p>© 2025 Casa Kolor. Todos los derechos reservados.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Quitar HTML para versión texto plano
            text_content = strip_tags(html_content)
            
            # Crear el correo electrónico
            email = EmailMultiAlternatives(
                asunto,
                text_content,
                settings.EMAIL_HOST_USER,
                [destinatario, 'hector3208609853@gmail.com']  # Cliente y correo de la empresa
            )
            
            # Adjuntar versión HTML
            email.attach_alternative(html_content, "text/html")
            
            # Si hay factura, adjuntarla al correo
            if hasattr(pedido, 'comprobante') and pedido.comprobante:
                email.attach_file(pedido.factura.path)
            
            # Enviar el correo
            email.send()
            
            # Guardar la transacción como procesada por 30 minutos
            cache.set(cache_key, True, 60 * 30)
            
            return JsonResponse({'success': True, 'message': 'Pedido creado correctamente y confirmación enviada por correo'})
        else:
            # Liberar la marca en caso de error
            cache.delete(cache_key)
            return JsonResponse({'success': False, 'errors': form.errors})
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

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


from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def perfil(request):
    return render(request, 'perfil.html')
