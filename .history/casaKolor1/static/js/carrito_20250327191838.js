document.addEventListener('DOMContentLoaded', () => {
    const cart = JSON.parse(localStorage.getItem('cart')) || [];
    const cartCountElement = document.getElementById('cart-count');
    const cartItemsContainer = document.getElementById('cart-items');
    const cartTotalElement = document.getElementById('cart-total');
    const clearCartBtn = document.getElementById('clear-cart-btn');

    // Verificar si el carrito está vacío al cargar la página
    if (cart.length === 0 && cartCountElement) {
        cartCountElement.style.display = 'none';
    }

    function restoreCartCount() {
        const savedCount = parseInt(localStorage.getItem('cartCount') || '0');
        if (cartCountElement) {
            cartCountElement.textContent = savedCount;
            // Forzar la visibilidad del contador basado en el valor
            if (savedCount <= 0) {
                cartCountElement.style.display = 'none';
            } else {
                cartCountElement.style.display = 'inline';
            }
        }
    }

    function updateCartCount() {
        const totalItems = cart.reduce((sum, item) => sum + item.cantidad, 0);
        localStorage.setItem('cartCount', totalItems); 
        if (cartCountElement) {
            cartCountElement.textContent = totalItems;
            // Forzar la visibilidad del contador basado en el valor
            if (totalItems <= 0) {
                cartCountElement.style.display = 'none';
            } else {
                cartCountElement.style.display = 'inline';
            }
        }
    }

    function renderCart() {
        if (cartItemsContainer) {
            cartItemsContainer.innerHTML = '';
            let total = 0;

            if (cart.length === 0) {
                const emptyRow = document.createElement('tr');
                emptyRow.innerHTML = `
                    <td colspan="6" class="text-center">No hay productos en el carrito</td>
                `;
                cartItemsContainer.appendChild(emptyRow);
                cartTotalElement.textContent = '0';
                
                // Asegurar que el contador esté oculto cuando el carrito está vacío
                if (cartCountElement) {
                    cartCountElement.textContent = '0';
                    cartCountElement.style.display = 'none';
                }
                return;
            }

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

    // Restaurar el contador al cargar la página
    restoreCartCount(); 

    // Agregar evento directamente al botón de limpiar carrito
    if (clearCartBtn) {
        clearCartBtn.addEventListener('click', function() {
            // Vaciar el carrito
            cart.length = 0;
            localStorage.removeItem('cart');
            localStorage.setItem('cartCount', '0');
            
            // Forzar la ocultación del contador
            if (cartCountElement) {
                cartCountElement.textContent = '0';
                cartCountElement.style.display = 'none';
            }
            
            renderCart();
        });
    }

    document.addEventListener('click', function (event) {
        if (event.target.classList.contains('add-to-cart') || event.target.closest('.add-to-cart')) {
            const card = event.target.closest('.card');
            const id = event.target.dataset.id || event.target.closest('.add-to-cart').dataset.id;
            const nombre = card.querySelector('.card-title').textContent;
            const descripcion = card.querySelector('.card-text').textContent;
            const precio = parseFloat(card.querySelector('.card-text strong').textContent.replace('Precio: $', '').replace(/\./g, '').replace(/,/g, '.'));
            const imagen = card.querySelector('img').src;

            const existingItem = cart.find(item => item.id === id);
            if (existingItem) {
                existingItem.cantidad++;
            } else {
                cart.push({ id, nombre, descripcion, precio, imagen, cantidad: 1 });
            }

            localStorage.setItem('cart', JSON.stringify(cart));
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

    // Iniciar con el contador actualizado según el estado actual del carrito
    renderCart();
    
    // Verificación adicional para asegurar que el contador esté correcto
    setTimeout(() => {
        const cartItems = JSON.parse(localStorage.getItem('cart')) || [];
        if (cartItems.length === 0 && cartCountElement) {
            cartCountElement.style.display = 'none';
        }
    }, 100);
});