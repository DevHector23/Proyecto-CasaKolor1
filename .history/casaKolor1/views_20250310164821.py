from .forms import UserRegistrationForm, CustomUserCreationForm, SugerenciaForm, PedidoForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from .models import productos, DetallePedido
from django.conf import settings
from django.db.models import Q
from django.core.mail import send_mail, EmailMultiAlternatives
from django.utils.html import strip_tags
from django.http import JsonResponse
from django.db import transaction
from django.core.cache import cache
import json
import logging
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'home.html')

def inicio(request):
    return render(request, 'inicio.html')

def productos_view(request):
    productos_list = productos.objects.all()
    return render(request, 'productos.html', {'productos': productos_list})

def carrito(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'Por favor, inicia sesión o regístrate para finalizar la compra.')
        return redirect('login')
    return render(request, 'carrito.html')

def lista_pinturas(request):
    lista_productos = productos.objects.filter(categoria='pinturas')
    return render(request, 'pinturas.html', {'productos': lista_productos})

def lista_herramientas(request):
    lista_herramientas = productos.objects.filter(categoria='herramientas')
    return render(request, 'herramientas.html', {'productos': lista_herramientas})

def mision(request):
    context = {'MEDIA_URL': settings.MEDIA_URL}
    return render(request, 'mision.html', context)

def buscar(request):
    query = request.GET.get('query', '')
    resultados = productos.objects.filter(
        Q(nombre__icontains=query) | Q(descripcion__icontains=query)
    return render(request, 'buscar.html', {'resultados': resultados, 'query': query})

def enviar_sugerencia(request):
    if request.method == "POST":
        form = SugerenciaForm(request.POST)
        if form.is_valid():
            sugerencia = form.save()
            form.send_email()
            return redirect('sugerencia_exitosa')
    else:
        form = SugerenciaForm()
    return render(request, 'sugerencias.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('inicio')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('inicio')

@login_required
def finalizar_compra(request):
    if request.method == 'POST':
        transaction_token = request.POST.get('transaction_token')
        cache_key = f'order_token_{transaction_token}'
        
        if cache.get(cache_key):
            return JsonResponse({'success': True, 'message': 'Pedido ya procesado'})
        
        cache.set(cache_key, True, 30)
        
        form = PedidoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    pedido = form.save(commit=False)
                    pedido.total = request.POST.get('total', 0)
                    
                    if 'comprobante' in request.FILES:
                        pedido.comprobante = request.FILES['comprobante']
                    
                    pedido.save()
                    
                    items = json.loads(request.POST.get('items', '[]'))
                    detalles_correo = []
                    
                    for item in items:
                        producto_id = item.get('id')
                        cantidad = item.get('cantidad', 1)
                        precio = item.get('precio', 0)
                        subtotal = item.get('subtotal', 0)
                        
                        try:
                            producto = productos.objects.get(id=producto_id)
                        except productos.DoesNotExist:
                            logger.error(f"Producto con ID {producto_id} no encontrado")
                            continue
                        
                        DetallePedido.objects.create(
                            pedido=pedido,
                            producto=producto,
                            cantidad=cantidad,
                            precio_unitario=precio,
                            subtotal=subtotal
                        )
                        
                        if producto.categoria == 'pinturas':
                            detalles_correo.append(f"Producto: {producto.nombre}, Presentación: {producto.get_presentacion_display()}, Cantidad: {cantidad}, Precio: ${precio}.")
                        else:
                            detalles_correo.append(f"Producto: {producto.nombre}, Cantidad: {cantidad}, Precio: ${precio}.")
                    
                    asunto = "Confirmación de Pedido - CasaKolor1"
                    mensaje = f"""
                    Hola {pedido.nombre},
                    
                    ¡Gracias por tu compra en CasaKolor1!
                    
                    Detalles de tu pedido:
                    {''.join([f'{chr(10)}- {detalle}' for detalle in detalles_correo])}
                    
                    Total: ${pedido.total}
                    
                    Tu pedido será procesado a la brevedad.
                    
                    Saludos,
                    El equipo de CasaKolor1
                    """
                    
                    destinatario = pedido.correo
                    
                    html_items = ""
                    for item in items:
                        producto_id = item.get('id')
                        cantidad = item.get('cantidad', 1)
                        precio = item.get('precio', 0)
                        try:
                            producto = productos.objects.get(id=producto_id)
                            if producto.categoria == 'pinturas':
                                html_items += f'<li>Producto: {producto.nombre}, Presentación: {producto.get_presentacion_display()}, Cantidad: {cantidad}, Precio: ${precio}.</li>'
                            else:
                                html_items += f'<li>Producto: {producto.nombre}, Cantidad: {cantidad}, Precio: ${precio}.</li>'
                        except productos.DoesNotExist:
                            logger.error(f"Producto con ID {producto_id} no encontrado")
                            continue
                    
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
                                <h3>Detalles de tu pedido:</h3>
                                <ul>
                                    {html_items}
                                </ul>
                                <p><strong>Total:</strong> ${pedido.total}</p>
                                
                                <h3>Comprobante de pago:</h3>
                                <p>Se ha recibido tu comprobante de pago.</p>
                                
                                <p>Tu pedido será procesado a la brevedad.</p>
                                <p>Saludos,<br>El equipo de CasaKolor1</p>
                                
                                <a href="#" class="button">Ver Detalles del Pedido</a>
                            </div>
                            <div class="footer">
                                <p>© 2025 CasaKolor1. Todos los derechos reservados.</p>
                            </div>
                        </div>
                    </body>
                    </html>
                    """
                    
                    text_content = strip_tags(html_content)
                    
                    email = EmailMultiAlternatives(
                        asunto,
                        text_content,
                        settings.EMAIL_HOST_USER,
                        [destinatario, 'ivanparrahernandez14@gmail.com']
                    )
                    
                    email.attach_alternative(html_content, "text/html")
                    
                    if hasattr(pedido, 'comprobante') and pedido.comprobante:
                        email.attach_file(pedido.comprobante.path)
                    
                    email.send()
                    
                    cache.set(cache_key, True, 60 * 30)
                    
                    return JsonResponse({'success': True, 'message': 'Pedido creado correctamente y confirmación enviada por correo'})
            except Exception as e:
                logger.error(f"Error al procesar el pedido: {e}")
                cache.delete(cache_key)
                return JsonResponse({'success': False, 'message': 'Error al procesar el pedido'})
        else:
            cache.delete(cache_key)
            return JsonResponse({'success': False, 'errors': form.errors})
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

def restablecer(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        
        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = request.build_absolute_uri(f'/cambiar-contraseña/{uid}/{token}/')
            send_mail(
                'Restablecimiento de contraseña',
                f'Haz clic en el siguiente enlace para restablecer tu contraseña: {reset_link}',
                'tucorreo@gmail.com',
                [email],
                fail_silently=False,