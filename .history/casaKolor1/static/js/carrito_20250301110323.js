document.getElementById('confirmarCompra').addEventListener('click', function() {
    // Obtener el formulario
    const form = document.getElementById('checkout-form');
    const formData = new FormData(form);
    
    // Añadir todos los campos necesarios
    formData.append('nombre', document.getElementById('nombre').value);
    formData.append('correo', document.getElementById('correo').value);
    formData.append('telefono', document.getElementById('telefono').value);
    formData.append('total', document.getElementById('cart-total').textContent);
    formData.append('items', JSON.stringify(getCartItems()));
    
    // Generar un token único para esta transacción
    formData.append('transaction_token', Date.now().toString() + Math.random().toString(36).substr(2, 9));
    
    // La factura ya debería estar incluida en el formData debido al enctype="multipart/form-data"
    
    // Enviar datos al servidor
    fetch('/finalizar-compra/', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Limpiar carrito y cerrar modal
            clearCart();
            $('#checkoutModal').modal('hide');
            alert('¡Compra realizada con éxito! Se ha enviado una confirmación a tu correo.');
        } else {
            alert('Error al procesar la compra: ' + JSON.stringify(data.errors));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al procesar la compra');
    });
});