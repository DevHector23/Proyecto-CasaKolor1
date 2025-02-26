document.getElementById('confirmarCompra').addEventListener('click', function () {
    const nombre = document.getElementById('nombre').value;
    const correo = document.getElementById('correo').value;
    const telefono = document.getElementById('telefono').value;
    const facturaInput = document.getElementById('factura');

    if (!nombre || !correo || !telefono) {
        alert('Por favor, complete todos los campos: nombre, correo y teléfono.');
        return;
    }

    if (!facturaInput || !facturaInput.files || facturaInput.files.length === 0) {
        alert('Por favor, suba una foto de la factura.');
        return;
    }

    const total = cart.reduce((sum, item) => sum + (item.precio * item.cantidad), 0);

    // Preparar los ítems con subtotales calculados
    const itemsWithSubtotal = cart.map(item => {
        return {
            id: item.id,
            nombre: item.nombre,
            descripcion: item.descripcion,
            precio: item.precio,
            cantidad: item.cantidad,
            subtotal: item.precio * item.cantidad
        };
    });

    const formData = new FormData();
    formData.append('nombre', nombre);
    formData.append('correo', correo);
    formData.append('telefono', telefono);
    formData.append('total', total);
    
    // Generar un token único para cada transacción
    const transactionToken = Date.now().toString() + Math.random().toString(36).substr(2, 9);
    formData.append('transaction_token', transactionToken);
    
    formData.append('items', JSON.stringify(itemsWithSubtotal));
    formData.append('comprobante', facturaInput.files[0]);

    const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfTokenElement) {
        formData.append('csrfmiddlewaretoken', csrfTokenElement.value);
    }

    // Mostrar indicador de carga
    const loadingIndicator = document.createElement('div');
    loadingIndicator.className = 'alert alert-info position-fixed top-0 start-50 translate-middle-x mt-3';
    loadingIndicator.style.zIndex = '9999';
    loadingIndicator.textContent = 'Procesando su compra, por favor espere...';
    document.body.appendChild(loadingIndicator);

    fetch('/finalizar-compra/', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error en la respuesta del servidor');
        }
        return response.json();
    })
    .then(data => {
        // Eliminar indicador de carga
        loadingIndicator.remove();
        
        if (data.success) {
            cart.length = 0;
            localStorage.removeItem('cart');
            localStorage.setItem('cartCount', 0);
            
            // Reemplazando el alert por un mensaje que no requiere interacción
            // y cierre automático del modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('checkoutModal'));
            modal.hide();
            
            // Crear una notificación temporal
            const notificacion = document.createElement('div');
            notificacion.className = 'alert alert-success position-fixed top-0 start-50 translate-middle-x mt-3';
            notificacion.style.zIndex = '9999';
            notificacion.textContent = '¡Compra realizada con éxito!';
            document.body.appendChild(notificacion);
            
            // Eliminar la notificación después de 3 segundos
            setTimeout(() => {
                notificacion.remove();
            }, 3000);
            
            renderCart();
        } else {
            let errorMessage = 'Error al procesar el pedido: ';
            if (data.errors) {
                Object.keys(data.errors).forEach(key => {
                    errorMessage += `\n${key}: ${data.errors[key]}`;
                });
            } else {
                errorMessage += data.message || 'Error desconocido';
            }
            alert(errorMessage);
        }
    })
    .catch(error => {
        // Eliminar indicador de carga en caso de error
        loadingIndicator.remove();
        console.error('Error:', error);
        alert('Error al procesar la compra. Por favor, inténtelo de nuevo.');
    });
});