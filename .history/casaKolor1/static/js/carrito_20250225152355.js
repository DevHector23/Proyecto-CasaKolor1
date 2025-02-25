document.addEventListener('DOMContentLoaded', () => {
    // Recuperar el carrito desde localStorage al cargar la página
    const cart = JSON.parse(localStorage.getItem('cart')) || [];
    const cartCountElement = document.getElementById('cart-count');
    const cartItemsContainer = document.getElementById('cart-items');
    const cartTotalElement = document.getElementById('cart-total');
    const modalCartItems = document.getElementById('modal-cart-items');
    const modalCartTotal = document.getElementById('modal-cart-total');

    // Restaurar el contador del carrito al cargar la página
    function restoreCartCount() {
        const savedCount = localStorage.getItem('cartCount');
        if (savedCount && cartCountElement) {
            cartCountElement.textContent = savedCount;
            cartCountElement.style.display = savedCount > 0 ? 'inline' : 'none';
        }
    }

    // Función para actualizar el contador del carrito
    function updateCartCount() {
        const totalItems = cart.reduce((sum, item) => sum + item.cantidad, 0);
        localStorage.setItem('cartCount', totalItems); // Guardar el contador en localStorage
        if (cartCountElement) {
            cartCountElement.textContent = totalItems;
            cartCountElement.style.display = totalItems > 0 ? 'inline' : 'none';
        }
    }

    // Función para renderizar el carrito en la página
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
        localStorage.setItem('cart', JSON.stringify(cart)); // Guardar el carrito en localStorage
        updateCartCount(); // Actualizar el contador del carrito
        renderModalCart(); // ✅ Asegurar que la modal también se actualice
    }

    // Función para renderizar los productos en la modal
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

    restoreCartCount(); // Restaurar el contador al cargar la página

    // Evento para agregar productos al carrito
    document.addEventListener('click', function (event) {
        if (event.target.classList.contains('add-to-cart')) {
            const card = event.target.closest('.card');
            const id = event.target.dataset.id;
            const nombre = card.querySelector('.card-title').textContent;
            const descripcion = card.querySelector('.card-text').textContent;
            const precio = parseFloat(card.querySelector('.card-text strong').textContent.replace('Precio: $', ''));
            const imagen = card.querySelector('img').src;

            const existingItem = cart.find(item => item.id === id);
            if (existingItem) {
                existingItem.cantidad++;
            } else {
                cart.push({ id, nombre, descripcion, precio, imagen, cantidad: 1 });
            }

            renderCart(); // Actualizar la vista del carrito
        }

        // Evento para eliminar productos del carrito
        if (event.target.closest('.remove-item')) {
            const button = event.target.closest('.remove-item');
            const id = button.dataset.id;
            const index = cart.findIndex(item => item.id === id);

            if (index !== -1) {
                cart.splice(index, 1);
                renderCart(); // Actualizar la vista del carrito
            }
        }

        // Evento para vaciar el carrito
        if (event.target.id === 'clear-cart-btn') {
            cart.length = 0;
            localStorage.removeItem('cart');
            localStorage.setItem('cartCount', 0); // Resetear el contador en localStorage
            renderCart(); // Actualizar la vista del carrito
        }

        // Evento para abrir la modal de finalizar compra
        if (event.target.id === 'btnFinalizarCompra') {
            renderModalCart(); // ✅ Se asegura que la modal se actualice al abrirla
        }
    });

    // Evento para cambiar la cantidad de un producto en el carrito
    document.addEventListener('change', function (event) {
        if (event.target.classList.contains('quantity-input')) {
            const id = event.target.dataset.id;
            const newQuantity = parseInt(event.target.value);
            const item = cart.find(item => item.id === id);

            if (item && newQuantity > 0) {
                item.cantidad = newQuantity;
                renderCart(); // Actualizar la vista del carrito
            }
        }
    });

    // Evento para confirmar la compra
    document.getElementById('confirmarCompra').addEventListener('click', function () {
        const nombre = document.getElementById('nombre').value;
        const correo = document.getElementById('correo').value;
        const telefono = document.getElementById('telefono').value;
        const factura = document.getElementById('factura').files[0];

        // Validar que los campos estén completos
        if (!nombre || !correo || !telefono) {
            alert('Por favor, complete todos los campos: nombre, correo y teléfono.');
            return;
        }

        // Validar que se haya subido una factura
        if (!factura) {
            alert('Por favor, suba una foto de la factura.');
            return;
        }

        // Crear un objeto con los datos del cliente y los productos
        const datosCliente = {
            nombre,
            correo,
            telefono,
            productos: cart,
            total: Math.floor(cart.reduce((sum, item) => sum + item.precio * item.cantidad, 0)).toLocaleString('es')
        };

        console.log('Datos del cliente:', datosCliente);
        alert('Compra confirmada. Gracias por su compra, ' + nombre + '!');

        // Limpiar el carrito y cerrar la modal
        cart.length = 0;
        localStorage.removeItem('cart');
        localStorage.setItem('cartCount', 0); // Resetear el contador en localStorage
        renderCart();
        bootstrap.Modal.getInstance(document.getElementById('checkoutModal')).hide();
    });

    // Renderizar el carrito y actualizar el contador al cargar la página
    renderCart();
});
