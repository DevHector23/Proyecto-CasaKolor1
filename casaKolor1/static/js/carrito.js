document.addEventListener('DOMContentLoaded', () => {
    const cart = JSON.parse(localStorage.getItem('cart')) || [];
    const cartCountElement = document.getElementById('cart-count');
    const cartItemsContainer = document.getElementById('cart-items');
    const cartTotalElement = document.getElementById('cart-total');

    const notificationContainer = document.createElement('div');
    notificationContainer.id = 'notification-container';
    notificationContainer.style.position = 'fixed';
    notificationContainer.style.top = '35px';
    notificationContainer.style.right = '125px';
    notificationContainer.style.zIndex = '9999';
    document.body.appendChild(notificationContainer);

    function showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.textContent = message;
        notification.style.backgroundColor = type === 'success' ? '#4CAF50' : '#f44336';
        notification.style.color = '#fff';
        notification.style.padding = '10px 20px';
        notification.style.marginBottom = '10px';
        notification.style.borderRadius = '5px';
        notification.style.boxShadow = '0 2px 6px rgba(0, 0, 0, 0.2)';
        notification.style.opacity = '1';
        notification.style.transition = 'opacity 0.5s ease';

        notificationContainer.appendChild(notification);

        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 500);
        }, 3000);
    }

    function updateCartCount() {
        const totalItems = cart.reduce((sum, item) => sum + item.cantidad, 0);
        cartCountElement.textContent = totalItems;
        cartCountElement.style.display = totalItems > 0 ? 'inline' : 'none';
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
                <button class="btn  btn-sm remove-item" data-id="${item.id}" aria-label="Eliminar">
                    <img src="${trashIconUrl}" alt="Eliminar" width="26">
                </button>
                    </td>
                `;
                cartItemsContainer.appendChild(row);
            });

            cartTotalElement.textContent = Math.floor(total).toLocaleString('es');
        }
        localStorage.setItem('cart', JSON.stringify(cart));
        updateCartCount();
    }

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

            showNotification('Producto añadido al carrito');
            renderCart();
        }

        if (event.target.closest('.remove-item')) {
            const button = event.target.closest('.remove-item');
            const id = button.dataset.id;
            const index = cart.findIndex(item => item.id === id);

            if (index !== -1) {
                cart.splice(index, 1);
                showNotification('Producto eliminado del carrito', 'error');
                renderCart();
            }
        }

        if (event.target.id === 'clear-cart-btn') {
            cart.length = 0;
            localStorage.removeItem('cart');
            showNotification('Todos los productos han sido eliminados del carrito', 'error');
            renderCart();
        }

        if (event.target.id === 'checkout-btn') {
            if (cart.length === 0) {
                showNotification('El carrito está vacío.', 'error');
                return;
            }

            showNotification('Compra realizada con éxito.');
            localStorage.removeItem('cart');
            window.location.href = '/';
        }
    });

    document.addEventListener('change', function (event) {
        if (event.target.classList.contains('quantity-input')) {
            const id = event.target.dataset.id;
            const newQuantity = parseInt(event.target.value);
            const item = cart.find(item => item.id === id);

            if (item && newQuantity > 0) {
                item.cantidad = newQuantity;
                renderCart();
            }
        }
    });

    renderCart();
    updateCartCount();
});
