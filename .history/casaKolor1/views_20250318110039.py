from .forms import UserRegistrationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from .models import productos
from django.conf import settings





def home(request):
    return render(request, 'home.html')


def productos_view(request):
    productos_list = productos.objects.all()
    return render(request, 'productos.html', {
        'productos': productos_list 
        
     })

def sugerencias(request):
    return render(request, 'sugerencias.html')

from django.contrib.auth.decorators import login_required




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
                return redirect('productos')
        # Si hay errores, simplemente continuamos para mostrar el formulario nuevamente
    
    # Siempre pasamos ambos formularios al template
    return render(request, 'login.html', {
        'form': login_form,
        'register_form': register_form
    })

from django.views.decorators.csrf import csrf_exempt
# También aplica el decorador a la vista de registro
@ensure_csrf_cookie
@csrf_exempt
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
    return redirect('home')  # Cambia esto por la URL a donde quieres redirigir

def logout_view(request):
    logout(request)
    return redirect('home')  # Redirige a la página principal




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



# Importaciones necesarias para las vistas
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
import json
import logging
import uuid
from .models import Pedido, DetallePedido, productos
from .forms import PedidoForm

logger = logging.getLogger(__name__)

@login_required
def carrito(request):
    return render(request, 'carrito.html')

@login_required
def pasarela_pago(request):
    return render(request, 'pasarela.html')

@login_required
def finalizar_compra(request):
    if request.method == 'POST':
        transaction_token = request.POST.get('transaction_token', str(uuid.uuid4()))
        cache_key = f'order_token_{transaction_token}'
        
        if cache.get(cache_key):
            return JsonResponse({'success': True, 'message': 'Pedido ya procesado'})
        
        cache.set(cache_key, True, 300) 
        
        form = PedidoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    if Pedido.objects.filter(transaction_id=transaction_token).exists():
                        return JsonResponse({'success': True, 'message': 'Pedido ya procesado'})
                    
                    pedido = form.save(commit=False)
                    pedido.total = request.POST.get('total', 0)
                    pedido.transaction_id = transaction_token
                    
                    if 'comprobante' in request.FILES:
                        pedido.comprobante = request.FILES['comprobante']
                    
                    pedido.save()
                    
                    items = json.loads(request.POST.get('items', '[]'))
                    
                    for item in items:
                        producto_id = item.get('id')
                        cantidad = int(item.get('cantidad', 1))
                        precio = float(item.get('precio', 0))
                        subtotal = precio * cantidad
                        
                        try:
                            producto = productos.objects.get(id=producto_id)
                            DetallePedido.objects.create(
                                pedido=pedido,
                                producto=producto,
                                cantidad=cantidad,
                                precio_unitario=precio,
                                subtotal=subtotal
                            )
                        except productos.DoesNotExist:
                            logger.error(f"Producto con ID {producto_id} no encontrado")
                            continue
                    
                    # Guardar en el historial de compras
                    HistorialCompra.objects.create(usuario=request.user, pedido=pedido)
                    
                    cache.set(cache_key, True, 60 * 30)  
                    
                    email_result = enviar_confirmacion_email_interno(pedido)
                    
                    if email_result.get('success'):
                        logger.info(f"Email enviado automáticamente para pedido {pedido.id}")
                    else:
                        logger.warning(f"Error al enviar email automático: {email_result.get('message')}")
                    
                    return JsonResponse({
                        'success': True, 
                        'message': 'Pedido creado correctamente', 
                        'pedido_id': pedido.id
                    })
            
            except Exception as e:
                logger.error(f"Error al procesar el pedido: {e}")
                if not str(e).lower().find("duplicate") >= 0:
                    cache.delete(cache_key)
                return JsonResponse({
                    'success': False, 
                    'message': f'Error al procesar el pedido: {str(e)}'
                })
        else:
            return JsonResponse({
                'success': False, 
                'errors': form.errors
            })
    
    return JsonResponse({
        'success': False, 
        'message': 'Método no permitido'
    })

from .models import Pedido
def enviar_confirmacion_email_interno(pedido):
    try:
        email_cache_key = f'email_sent_{pedido.id}'
        
        if cache.get(email_cache_key):
            logger.info(f"Correo ya enviado previamente para el pedido ID {pedido.id}")
            return {'success': True, 'message': 'Email ya enviado'}
        
        if not pedido.correo:
            logger.error(f"Correo de usuario vacío para pedido ID {pedido.id}")
            return {'success': False, 'message': 'Correo de usuario no válido'}
            
        detalles = DetallePedido.objects.filter(pedido=pedido)
        
        html_items = ""
        for detalle in detalles:
            producto = detalle.producto
            if producto and producto.categoria == 'pinturas':
                html_items += f'<li>Producto: {producto.nombre}, Presentación: {producto.get_presentacion_display()}, Cantidad: {detalle.cantidad}, Precio: ${detalle.precio_unitario}.</li>'
            elif producto:
                html_items += f'<li>Producto: {producto.nombre}, Cantidad: {detalle.cantidad}, Precio: ${detalle.precio_unitario}.</li>'
            else:
                html_items += f'<li>Producto no disponible, Cantidad: {detalle.cantidad}, Precio: ${detalle.precio_unitario}.</li>'
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; background-color: #f4f4f4; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 20px auto; padding: 20px; background-color: #ffffff; border-radius: 10px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .header h2 {{ margin: 0; font-size: 24px; }}
                .content {{ padding: 20px; }}
                .content h3 {{ color: #4CAF50; font-size: 20px; margin-bottom: 10px; }}
                .content ul {{ list-style-type: none; padding: 0; }}
                .content ul li {{ background-color: #f9f9f9; margin: 5px 0; padding: 10px; border-left: 5px solid #4CAF50; }}
                .content p {{ margin: 10px 0; }}
                .footer {{ font-size: 12px; color: #777; text-align: center; margin-top: 20px; }}
                .footer p {{ margin: 0; }}
                .button {{ display: inline-block; padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Confirmación de Pedido - CasaKolor1</h2>
                </div>
                <div class="content">
                    <p>Hola {pedido.nombre},</p>
                    <p>¡Gracias por tu compra en CasaKolor1!</p>
                    <h3>Detalles de tu pedido (#{pedido.id}):</h3>
                    <ul>
                        {html_items}
                    </ul>
                    <p><strong>Total:</strong> ${pedido.total}</p>
                    
                    <h3>Comprobante de pago:</h3>
                    <p>Se ha recibido tu comprobante de pago correctamente.</p>
                    
                    <p>Tu pedido será procesado a la brevedad. Te contactaremos cuando esté listo para entrega o recogida.</p>
                    <p>Si tienes alguna pregunta, responde a este correo directamente.</p>
                    <p>Saludos,<br>El equipo de CasaKolor1</p>
                </div>
                <div class="footer">
                    <p>© 2025 CasaKolor1. Todos los derechos reservados.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = strip_tags(html_content)
        
        if not all([settings.EMAIL_HOST, settings.EMAIL_PORT, settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD]):
            logger.error("Configuración de email incompleta en settings.py")
            return {'success': False, 'message': 'Configuración de email incompleta en el servidor'}
        
        admin_email = 'hector3208609853@gmail.com'
        
        try:
            logger.info(f"Intentando enviar correo para pedido ID {pedido.id} a usuario: '{pedido.correo}' y admin: '{admin_email}'")

            user_email = EmailMultiAlternatives(
                "Confirmación de Pedido - CasaKolor1",
                text_content,
                settings.EMAIL_HOST_USER,
                [pedido.correo]
            )
            user_email.attach_alternative(html_content, "text/html")
            
            if hasattr(pedido, 'comprobante') and pedido.comprobante:
                try:
                    user_email.attach_file(pedido.comprobante.path)
                except Exception as e:
                    logger.warning(f"No se pudo adjuntar comprobante al correo del usuario: {e}")

            try:
                user_email.send(fail_silently=False)
                logger.info(f"Correo enviado correctamente al usuario {pedido.correo} para pedido ID {pedido.id}")
                user_email_sent = True
            except Exception as e:
                logger.error(f"Error al enviar correo al usuario {pedido.correo}: {e}")
                user_email_sent = False
            
            admin_email_obj = EmailMultiAlternatives(
                f"[ADMIN] Nueva Orden #{pedido.id} - CasaKolor1",
                text_content,
                settings.EMAIL_HOST_USER,
                [admin_email]
            )
            admin_email_obj.attach_alternative(html_content, "text/html")
            
            if hasattr(pedido, 'comprobante') and pedido.comprobante:
                try:
                    admin_email_obj.attach_file(pedido.comprobante.path)
                except Exception as e:
                    logger.warning(f"No se pudo adjuntar comprobante al correo del admin: {e}")
            
            try:
                admin_email_obj.send(fail_silently=False)
                logger.info(f"Correo enviado correctamente al administrador {admin_email} para pedido ID {pedido.id}")
                admin_email_sent = True
            except Exception as e:
                logger.error(f"Error al enviar correo al administrador {admin_email}: {e}")
                admin_email_sent = False
            
            if user_email_sent or admin_email_sent:
                cache.set(email_cache_key, True, 60 * 60 * 24)  
                
                success_message = []
                if user_email_sent:
                    success_message.append("Email enviado al usuario")
                if admin_email_sent:
                    success_message.append("Email enviado al administrador")
                
                return {'success': True, 'message': '; '.join(success_message)}
            else:
                return {'success': False, 'message': 'No se pudo enviar ningún correo'}
                
        except Exception as e:
            logger.error(f"Error general al enviar correos: {e}")
            return {'success': False, 'message': f'Error al enviar emails: {str(e)}'}
        
    except Exception as e:
        logger.error(f"Error no controlado en enviar_confirmacion_email_interno: {e}")
        return {'success': False, 'message': f'Error: {str(e)}'}

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
