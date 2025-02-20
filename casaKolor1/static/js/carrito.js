document.addEventListener('DOMContentLoaded', () => {
    const cart = JSON.parse(localStorage.getItem('cart')) || [];
    const cartCountElement = document.getElementById('cart-count');
    const cartItemsContainer = document.getElementById('cart-items');
    const cartTotalElement = document.getElementById('cart-total');

    function updateCartCount() {
        const totalItems = cart.reduce((sum, item) => sum + item.cantidad, 0);
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

            renderCart();
        }

        if (event.target.closest('.remove-item')) {
            const button = event.target.closest('.remove-item');
            const id = button.dataset.id;
            const index = cart.findIndex(item => item.id === id);

            if (index !== -1) {
                cart.splice(index, 1);
                renderCart();
            }
        }

        if (event.target.id === 'clear-cart-btn') {
            cart.length = 0;
            localStorage.removeItem('cart');
            renderCart();
        }

        if (event.target.id === 'checkout-btn') {
            if (cart.length === 0) {
                return;
            }

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
