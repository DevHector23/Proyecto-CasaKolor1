document.addEventListener('DOMContentLoaded', () => {
    const cart = JSON.parse(localStorage.getItem('cart')) || [];
    const cartCountElement = document.getElementById('cart-count');
    const cartItemsContainer = document.getElementById('cart-items');
    const cartTotalElement = document.getElementById('cart-total');
    const modalCartItems = document.getElementById('modal-cart-items');
    const modalCartTotal = document.getElementById('modal-cart-total');

    function updateCartCount() {
        const totalItems = cart.reduce((sum, item) => sum + item.cantidad, 0);
        localStorage.setItem('cartCount', totalItems);
        if (cartCountElement) {
            cartCountElement.textContent = totalItems;
            cartCountElement.style.display = totalItems > 0 ? 'inline' : 'none';
        }
    }

    function renderCart() {
        if (cartItemsContainer) {
            cartItemsContainer.innerHTML = '';
            let total = 0;

            cart.forEach(item => {
                const subtotal = item.precio * item.cantidad;
                total += subtotal;

                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${item.nombre}</td>
                    <td>${item.descripcion}</td>
                    <td>$${item.precio.toLocaleString('es')}</td>
                    <td>
                        <input type="number" min="1" value="${item.cantidad}" class="form-control quantity-input" data-id="${item.id}">
                    </td>
                    <td>$${Math.floor(subtotal).toLocaleString('es')}</td>
                    <td>
                        <button class="btn btn-sm remove-item" data-id="${item.id}" aria-label="Eliminar">
                            <img src="/static/images/basura.png" alt="Eliminar" width="26">
                        </button>
                    </td>
                `;
                cartItemsContainer.appendChild(row);
            });

            cartTotalElement.textContent = Math.floor(total).toLocaleString('es');
        }
        localStorage.setItem('cart', JSON.stringify(cart)); 
        updateCartCount(); 
        renderModalCart(); 
    }

    function renderModalCart() {
        if (modalCartItems && modalCartTotal) {
            modalCartItems.innerHTML = '';
            let total = 0;

            cart.forEach(item => {
                const subtotal = item.precio * item.cantidad;
                total += subtotal;

                const li = document.createElement('li');
                li.innerHTML = `
                    <strong>${item.nombre}</strong><br>
                    <small>${item.descripcion}</small><br>
                    $${item.precio.toLocaleString('es')} x ${item.cantidad} = $${Math.floor(subtotal).toLocaleString('es')}
                `;
                modalCartItems.appendChild(li);
            });

            modalCartTotal.textContent = `$${Math.floor(total).toLocaleString('es')}`;
        }
    }

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

        const formData = new FormData();
        formData.append('nombre', nombre);
        formData.append('correo', correo);
        formData.append('telefono', telefono);
        formData.append('total', total);
        formData.append('items', JSON.stringify(cart));
        formData.append('comprobante', facturaInput.files[0]);

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
                // Limpiar carrito correctamente
                cart.length = 0;
                localStorage.removeItem('cart');
                localStorage.setItem('cartCount', 0);
                
                // Cerrar el modal de compra
                const modalElement = document.getElementById('checkoutModal');
                const modalInstance = bootstrap.Modal.getInstance(modalElement);
                modalInstance.hide();

                // Crear un mensaje de éxito sin alert
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
            console.error('Error:', error);
            alert('Error al procesar la compra. Por favor, inténtelo de nuevo.');
        });
    });

    renderCart();
});
