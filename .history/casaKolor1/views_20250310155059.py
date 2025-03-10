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

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Table, TableStyle
from django.http import HttpResponse
from django.urls import reverse

def finalizar_compra(request):
    if request.method == 'POST':
        transaction_token = request.POST.get('transaction_token')
        cache_key = f'order_token_{transaction_token}'
        
        if cache.get(cache_key):
            return JsonResponse({'success': True, 'message': 'Pedido ya procesado'})
        
        cache.set(cache_key, True, 30)
        
        form = PedidoForm(request.POST, request.FILES)
        if form.is_valid():
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
                
                producto = productos.objects.get(id=producto_id)
                
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
            
            # Redirigir a la factura en PDF
            return redirect(reverse('generar_factura_pdf', args=[pedido.id]))
        else:
            cache.delete(cache_key)
            return JsonResponse({'success': False, 'errors': form.errors})
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

# Vista para generar la factura en PDF
def generar_factura_pdf(request, pedido_id):
    # Obtener el pedido y sus detalles
    pedido = Pedido.objects.get(id=pedido_id)
    detalles = DetallePedido.objects.filter(pedido=pedido)

    # Crear un objeto HttpResponse con el tipo de contenido PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="factura_{pedido.id}.pdf"'

    # Crear el PDF con ReportLab
    p = canvas.Canvas(response, pagesize=letter)

    # Configurar el estilo del texto
    styles = getSampleStyleSheet()
    style_normal = styles['Normal']

    # Agregar contenido al PDF
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, f"Factura #{pedido.id}")

    p.setFont("Helvetica", 12)
    p.drawString(100, 730, f"Cliente: {pedido.nombre}")
    p.drawString(100, 710, f"Correo: {pedido.correo}")
    p.drawString(100, 690, f"Fecha: {pedido.fecha_compra}")

    # Crear una tabla para los detalles del pedido
    data = [['Producto', 'Cantidad', 'Precio Unitario', 'Subtotal']]
    for detalle in detalles:
        data.append([
            detalle.producto.nombre,
            detalle.cantidad,
            f"${detalle.precio_unitario}",
            f"${detalle.subtotal}",
        ])

    # Crear la tabla
    table = Table(data, colWidths=[200, 80, 100, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Dibujar la tabla en el PDF
    table.wrapOn(p, 400, 600)
    table.drawOn(p, 100, 550)

    # Agregar el total
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, 500, f"Total: ${pedido.total}")

    # Finalizar el PDF
    p.showPage()
    p.save()

    return response

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
