document.getElementById('confirmarCompra').addEventListener('click', function () {
    if (this.disabled) return;
    this.disabled = true; // Evitar doble clic

    const nombre = document.getElementById('nombre').value;
    const correo = document.getElementById('correo').value;
    const telefono = document.getElementById('telefono').value;
    const facturaInput = document.getElementById('factura');

    if (!nombre || !correo || !telefono) {
        alert('Por favor, complete todos los campos.');
        this.disabled = false;
        return;
    }

    if (!facturaInput || !facturaInput.files || facturaInput.files.length === 0) {
        alert('Por favor, suba una foto de la factura.');
        this.disabled = false;
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
    formData.append('transaction_token', Date.now().toString()); // Token único para evitar duplicados

    const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfTokenElement) {
        formData.append('csrfmiddlewaretoken', csrfTokenElement.value);
    }

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
            alert(data.message);
        }
        document.getElementById('confirmarCompra').disabled = false;
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al procesar la compra. Inténtelo de nuevo.');
        document.getElementById('confirmarCompra').disabled = false;
    });
});
