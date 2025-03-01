from django.shortcuts import render
from .models import productos, PrecioPresentacion

def lista_pinturas(request):
    # Obtener todas las pinturas con sus precios por presentación precargados
    lista_productos = productos.objects.filter(categoria='pinturas').prefetch_related('precios_presentacion')
    return render(request, 'pinturas.html', {'productos': lista_productos})

def productos_view(request):
    # Obtener todos los productos, incluyendo las pinturas con sus presentaciones
    productos_list = productos.objects.all().prefetch_related('precios_presentacion')
    return render(request, 'productos.html', {'productos': productos_list})

# Actualizar la vista de finalizar compra para manejar los datos de presentación
from django.http import JsonResponse
from .models import Pedido, DetallePedido
from .forms import PedidoForm
import json
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
        cache.set(cache_key, True, 30)
        
        form = PedidoForm(request.POST, request.FILES)
        if form.is_valid():
            # Crear el pedido
            pedido = form.save(commit=False)
            pedido.total = request.POST.get('total', 0)
            pedido.save()
            
            # Procesar los productos del carrito
            items = json.loads(request.POST.get('items', '[]'))
            detalles_correo = []
            
            for item in items:
                producto_id = item.get('id')
                cantidad = item.get('cantidad', 1)
                precio = item.get('precio', 0)
                subtotal = item.get('subtotal', 0)
                presentacion = item.get('presentacion')  # Obtener la presentación
                
                producto = productos.objects.get(id=producto_id)
                
                # Crear detalle del pedido incluyendo la presentación
                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=precio,
                    subtotal=subtotal,
                    presentacion=presentacion  # Guardar la presentación
                )
                
                # Agregar información para el correo incluyendo la presentación si existe
                presentacion_info = ""
                if presentacion:
                    for precio_pres in producto.precios_presentacion.all():
                        if precio_pres.presentacion == presentacion:
                            presentacion_info = f", Presentación: {precio_pres.get_presentacion_display()}"
                            break
                
                detalles_correo.append(f"Producto: {producto.nombre}{presentacion_info}, Cantidad: {cantidad}, Precio: ${precio}.")
            
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
            send_mail(asunto, mensaje, settings.EMAIL_HOST_USER, [destinatario])
            
            # Guardar la transacción como procesada por 30 minutos
            cache.set(cache_key, True, 60 * 30)
            
            return JsonResponse({'success': True, 'message': 'Pedido creado correctamente y confirmación enviada por correo'})
        else:
            # Liberar la marca en caso de error
            cache.delete(cache_key)
            return JsonResponse({'success': False, 'errors': form.errors})
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})