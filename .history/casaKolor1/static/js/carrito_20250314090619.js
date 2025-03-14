def finalizar_compra(request):
    if request.method == 'POST':
        transaction_token = request.POST.get('transaction_token')
        cache_key = f'order_token_{transaction_token}'
        
        # Verificar si esta orden ya fue procesada
        if cache.get(cache_key):
            return JsonResponse({'success': True, 'message': 'Pedido ya procesado'})
        
        # Establecer un bloqueo temporal para evitar procesamiento duplicado
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
                    
                    # Procesar los items del pedido
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
                    
                    # Actualizar la caché para evitar procesamiento duplicado antes de enviar el correo
                    cache.set(cache_key, True, 60 * 30)  # 30 minutos
                    
                    # Responder primero al cliente antes de enviar el correo
                    response = JsonResponse({'success': True, 'message': 'Pedido creado correctamente'})
                    
                    # Preparar el correo en segundo plano
                    asunto = "Confirmación de Pedido - CasaKolor1"
                    
                    # Preparar contenido HTML para el correo
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
                    
                    # Enviar el correo
                    try:
                        email = EmailMultiAlternatives(
                            asunto,
                            text_content,
                            settings.EMAIL_HOST_USER,
                            [pedido.correo, 'ivanparrahernandez14@gmail.com']
                        )
                        
                        email.attach_alternative(html_content, "text/html")
                        
                        if hasattr(pedido, 'comprobante') and pedido.comprobante:
                            email.attach_file(pedido.comprobante.path)
                        
                        email.send(fail_silently=True)  # Enviar sin arrojar excepciones
                    except Exception as e:
                        logger.error(f"Error al enviar correo: {e}")
                        # No devolveremos error al cliente porque el pedido ya está creado
                    
                    return response
                    
            except Exception as e:
                logger.error(f"Error al procesar el pedido: {e}")
                cache.delete(cache_key)
                return JsonResponse({'success': False, 'message': f'Error al procesar el pedido: {str(e)}'})
        else:
            cache.delete(cache_key)
            return JsonResponse({'success': False, 'errors': form.errors})
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})