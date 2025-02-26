document.getElementById('confirmarCompra').addEventListener('click', function (event) {
    // Prevenir múltiples clics
    const button = event.currentTarget;
    if (button.disabled) return;
    button.disabled = true;
    
    // Generar un token único para esta transacción
    const transactionToken = Date.now() + '-' + Math.random().toString(36).substring(2, 15);
    
    const nombre = document.getElementById('nombre').value;
    const correo = document.getElementById('correo').value;
    const telefono = document.getElementById('telefono').value;
    const facturaInput = document.getElementById('factura');

    if (!nombre || !correo || !telefono) {
        alert('Por favor, complete todos los campos: nombre, correo y teléfono.');
        button.disabled = false;
        return;
    }

    if (!facturaInput || !facturaInput.files || facturaInput.files.length === 0) {
        alert('Por favor, suba una foto de la factura.');
        button.disabled = false;
        return;
    }

    const total = cart.reduce((sum, item) => sum + (item.precio * item.cantidad), 0);

    const formData = new FormData();
    formData.append('nombre', nombre);
    formData.append('correo', correo);
    formData.append('telefono', telefono);
    formData.append('total', total);
    formData.append('items', JSON.stringify(cart));
    formData.append('comprobante', facturaInput.files[0]);
    formData.append('transaction_token', transactionToken); // Añadir el token único

    const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfTokenElement) {
        formData.append('csrfmiddlewaretoken', csrfTokenElement.value);
    }

    // Guardar el token en localStorage para tener una referencia
    localStorage.setItem('last_transaction', transactionToken);

    fetch('/finalizar-compra/', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            cart.length = 0;
            localStorage.removeItem('cart');
            localStorage.setItem('cartCount', 0);
            
            alert('¡Compra realizada con éxito!');
            
            const modal = bootstrap.Modal.getInstance(document.getElementById('checkoutModal'));
            modal.hide();
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
        // Reactivar el botón después de procesar
        button.disabled = false;
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al procesar la compra. Por favor, inténtelo de nuevo.');
        button.disabled = false;
    });
});