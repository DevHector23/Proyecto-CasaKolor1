document.addEventListener('DOMContentLoaded', () => {
    const cart = JSON.parse(localStorage.getItem('cart')) || [];
    const cartCountElement = document.getElementById('cart-count');
    const cartItemsContainer = document.getElementById('cart-items');
    const cartTotalElement = document.getElementById('cart-total');
    const modalCartItems = document.getElementById('modal-cart-items');
    const modalCartTotal = document.getElementById('modal-cart-total');

    function restoreCartCount() {
        const savedCount = localStorage.getItem('cartCount');
        if (savedCount && cartCountElement) {
            cartCountElement.textContent = savedCount;
            cartCountElement.style.display = savedCount > 0 ? 'inline' : 'none';
        }
    }

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

    restoreCartCount();

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

        if (event.target.id === 'clear-cart-btn') {
            cart.length = 0;
            localStorage.removeItem('cart');
            localStorage.setItem('cartCount', 0); 
            renderCart();
        }

        if (event.target.id === 'btnFinalizarCompra') {
            renderModalCart(); 
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

    // Variable para controlar si hay una compra en proceso
    let compraEnProceso = false;

    // Verificar si el elemento existe antes de agregar el event listener
    const confirmarCompraBtn = document.getElementById('confirmarCompra');
    if (confirmarCompraBtn) {
        confirmarCompraBtn.addEventListener('click', function () {
            // Evitar múltiples envíos
            if (compraEnProceso) {
                return;
            }

            const nombre = document.getElementById('nombre').value;
            const correo = document.getElementById('correo').value;
            const telefono = document.getElementById('telefono').value;
            const facturaInput = document.getElementById('factura');

            // Validación de campos
            if (!nombre || !correo || !telefono) {