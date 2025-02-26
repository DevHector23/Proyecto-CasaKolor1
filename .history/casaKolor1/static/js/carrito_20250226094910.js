// Al principio del archivo carrito.js
let compraEnProceso = false;

document.addEventListener('DOMContentLoaded', function() {
    // Elimina cualquier evento previo
    const confirmarBtn = document.getElementById('confirmarCompra');
    if (confirmarBtn) {
        const nuevoBtn = confirmarBtn.cloneNode(true);
        confirmarBtn.parentNode.replaceChild(nuevoBtn, confirmarBtn);
        
        // Adjunta el nuevo evento
        nuevoBtn.addEventListener('click', function(e) {
            if (compraEnProceso) return; // Evita múltiples envíos
            compraEnProceso = true;
            
            // Deshabilita el botón
            this.disabled = true;
            this.innerHTML = 'Procesando...';
            
            // Tu código existente para enviar la compra
            procesarCompra();
        });
    }
});

function procesarCompra() {
    // Código existente para procesar la compra
    const form = document.getElementById('checkout-form');
    const formData = new FormData(form);
    
    // Añadir datos del carrito
    // ...
    
    fetch('/procesar-compra/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-No-Duplicates': 'true', // Cabecera personalizada
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Mostrar mensaje de éxito
            vaciarCarrito();
            $('#checkoutModal').modal('hide');
            alert(data.message);
            // O mejor usar una notificación más elegante
        } else {
            alert(data.error || 'Error al procesar la compra');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Ocurrió un error al procesar tu compra');
    })
    .finally(() => {
        // Habilitar el botón nuevamente
        const confirmarBtn = document.getElementById('confirmarCompra');
        if (confirmarBtn) {
            confirmarBtn.disabled = false;
            confirmarBtn.innerHTML = 'Confirmar Compra';
        }
        compraEnProceso = false;
    });
}