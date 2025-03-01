// Función para mostrar los detalles del producto en el modal
function updateModalCartItems() {
    const cartItems = getCartItems();
    const modalCartItemsContainer = document.getElementById('modal-cart-items');
    const modalCartTotal = document.getElementById('modal-cart-total');
    
    // Limpiar contenedor
    modalCartItemsContainer.innerHTML = '';
    
    // Actualizar elementos
    let total = 0;
    
    cartItems.forEach(item => {
        const listItem = document.createElement('li');
        
        // Determinar si es una pintura para mostrar presentación
        let presentacion = '';
        if (item.categoria && item.categoria.toLowerCase() === 'pinturas') {
            // Buscar información sobre la presentación en el nombre o descripción
            const nombreLower = item.nombre.toLowerCase();
            const descLower = (item.descripcion || '').toLowerCase();
            
            if (nombreLower.includes('galón') || nombreLower.includes('galon') || 
                descLower.includes('galón') || descLower.includes('galon')) {
                presentacion = "Galón";
            } else if (nombreLower.includes('cuarto') || descLower.includes('cuarto')) {
                presentacion = "Cuarto de galón";
            } else if (nombreLower.includes('litro') || descLower.includes('litro')) {
                presentacion = "Litro";
            } else {
                presentacion = "Unidad";
            }
        }
        
        listItem.innerHTML = `
            <strong>${item.nombre}</strong>
            ${presentacion ? `<br>Presentación: ${presentacion}` : ''}
            <br>Cantidad: ${item.cantidad}
            <br>Precio: $${item.precio}
            <br>Subtotal: $${item.subtotal}
            ${item.descripcion ? `<br><small>Descripción: ${item.descripcion}</small>` : ''}
        `;
        
        modalCartItemsContainer.appendChild(listItem);
        total += parseFloat(item.subtotal);
    });
    
    // Actualizar total
    modalCartTotal.textContent = `$${total.toFixed(2)}`;
}

// Función para agregar un producto al carrito
function addToCart(id, nombre, precio, imagen, categoria, descripcion) {
    let cart = JSON.parse(localStorage.getItem('cart')) || [];
    
    // Buscar si el producto ya está en el carrito
    const existingProductIndex = cart.findIndex(item => item.id === id);
    
    if (existingProductIndex >= 0) {
        // Actualizar cantidad
        cart[existingProductIndex].cantidad += 1;
        cart[existingProductIndex].subtotal = (cart[existingProductIndex].cantidad * parseFloat(cart[existingProductIndex].precio)).toFixed(2);
    } else {
        // Agregar nuevo producto
        cart.push({
            id: id,
            nombre: nombre,
            precio: precio,
            imagen: imagen,
            cantidad: 1,
            subtotal: precio,
            categoria: categoria,
            descripcion: descripcion
        });
    }
    
    // Guardar en localStorage
    localStorage.setItem('cart', JSON.stringify(cart));
    
    // Actualizar contador del carrito
    updateCartCounter();
    
    // Mostrar notificación
    alert('Producto agregado al carrito');
}

// Función para obtener los items del carrito
function getCartItems() {
    return JSON.parse(localStorage.getItem('cart')) || [];
}

// Función para renderizar los items del carrito en la tabla
function renderCartItems() {
    const cartItemsContainer = document.getElementById('cart-items');
    const cartTotal = document.getElementById('cart-total');
    
    if (!cartItemsContainer) return; // Si no estamos en la página del carrito
    
    // Limpiar contenedor
    cartItemsContainer.innerHTML = '';
    
    // Obtener productos del carrito
    const cartItems = getCartItems();
    
    // Si el carrito está vacío
    if (cartItems.length === 0) {
        cartItemsContainer.innerHTML = '<tr><td colspan="6" class="text-center">Tu carrito está vacío</td></tr>';
        cartTotal.textContent = '0.00';
        return;
    }
    
    // Renderizar productos
    let total = 0;
    
    cartItems.forEach(item => {
        const row = document.createElement('tr');
        
        row.innerHTML = `
            <td>
                <img src="${item.imagen}" alt="${item.nombre}" class="cart-item-image">
            </td>
            <td>
                <div>${item.nombre}</div>
                ${item.descripcion ? `<small>${item.descripcion}</small>` : ''}
                ${item.categoria === 'pinturas' ? `<div><small>Categoría: Pinturas</small></div>` : ''}
            </td>
            <td>$${item.precio}</td>
            <td>
                <div class="quantity-controls">
                    <button class="btn btn-sm btn-quantity" data-id="${item.id}" data-action="decrease">-</button>
                    <span class="quantity-value">${item.cantidad}</span>
                    <button class="btn btn-sm btn-quantity" data-id="${item.id}" data-action="increase">+</button>
                </div>
            </td>
            <td>$${item.subtotal}</td>
            <td>
                <button class="btn btn-remove" data-id="${item.id}">
                    <img src="${trashIconUrl}" alt="Eliminar" class="trash-icon">
                </button>
            </td>
        `;
        
        cartItemsContainer.appendChild(row);
        total += parseFloat(item.subtotal);
    });
    
    // Actualizar total
    cartTotal.textContent = total.toFixed(2);
}

// Event listener para cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    // Renderizar items del carrito
    renderCartItems();
    
    // Actualizar contador del carrito
    updateCartCounter();
    
    // Botón para vaciar carrito
    const clearCartBtn = document.getElementById('clear-cart-btn');
    if (clearCartBtn) {
        clearCartBtn.addEventListener('click', function() {
            if (confirm('¿Estás seguro de que deseas vaciar el carrito?')) {
                clearCart();
                renderCartItems();
                updateCartCounter();
            }
        });
    }
    
    // Botones de incremento/decremento de cantidad
    const cartItemsContainer = document.getElementById('cart-items');
    if (cartItemsContainer) {
        cartItemsContainer.addEventListener('click', function(event) {
            if (event.target.classList.contains('btn-quantity')) {
                const button = event.target;
                const id = button.getAttribute('data-id');
                const action = button.getAttribute('data-action');
                
                updateQuantity(id, action);
                renderCartItems();
            }
            
            if (event.target.classList.contains('btn-remove') || event.target.parentElement.classList.contains('btn-remove')) {
                const button = event.target.classList.contains('btn-remove') ? event.target : event.target.parentElement;
                const id = button.getAttribute('data-id');
                
                removeFromCart(id);
                renderCartItems();
                updateCartCounter();
            }
        });
    }
    
    // Modal de finalizar compra
    const checkoutModal = document.getElementById('checkoutModal');
    if (checkoutModal) {
        // Actualizar modal cuando se muestra
        checkoutModal.addEventListener('show.bs.modal', function() {
            updateModalCartItems();
        });
        
        // Botón de confirmar compra
        const confirmarCompraBtn = document.getElementById('confirmarCompra');
        if (confirmarCompraBtn) {
            confirmarCompraBtn.addEventListener('click', function() {
                // Validar que hay productos en el carrito
                const cartItems = getCartItems();
                if (cartItems.length === 0) {
                    alert('Tu carrito está vacío');
                    return;
                }
                
                // Validar campos del formulario
                const nombre = document.getElementById('nombre').value;
                const correo = document.getElementById('correo').value;
                const telefono = document.getElementById('telefono').value;
                const factura = document.getElementById('factura').files[0];
                
                if (!nombre || !correo || !telefono) {
                    alert('Por favor completa todos los campos obligatorios');
                    return;
                }
                
                if (!factura) {
                    alert('Por favor sube una imagen de tu comprobante de pago');
                    return;
                }
                
                // Obtener el formulario
                const form = document.getElementById('checkout-form');
                const formData = new FormData(form);
                
                // Añadir todos los campos necesarios
                formData.append('nombre', nombre);
                formData.append('correo', correo);
                formData.append('telefono', telefono);
                formData.append('total', document.getElementById('cart-total').textContent);
                formData.append('items', JSON.stringify(cartItems));
                
                // Generar un token único para esta transacción
                formData.append('transaction_token', Date.now().toString() + Math.random().toString(36).substr(2, 9));
                
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
                        const bsModal = bootstrap.Modal.getInstance(checkoutModal);
                        bsModal.hide();
                        alert('¡Compra realizada con éxito! Se ha enviado una confirmación a tu correo.');
                        renderCartItems();
                        updateCartCounter();
                    } else {
                        alert('Error al procesar la compra: ' + JSON.stringify(data.errors));
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error al procesar la compra');
                });
            });
        }
    }
});

// Función para actualizar cantidad
function updateQuantity(id, action) {
    let cart = JSON.parse(localStorage.getItem('cart')) || [];
    
    const productIndex = cart.findIndex(item => item.id === id);
    
    if (productIndex >= 0) {
        if (action === 'increase') {
            cart[productIndex].cantidad += 1;
        } else if (action === 'decrease') {
            if (cart[productIndex].cantidad > 1) {
                cart[productIndex].cantidad -= 1;
            } else {
                return; // No reducir por debajo de 1
            }
        }
        
        // Actualizar subtotal
        cart[productIndex].subtotal = (cart[productIndex].cantidad * parseFloat(cart[productIndex].precio)).toFixed(2);
        
        // Guardar en localStorage
        localStorage.setItem('cart', JSON.stringify(cart));
    }
}

// Función para eliminar un producto del carrito
function removeFromCart(id) {
    let cart = JSON.parse(localStorage.getItem('cart')) || [];
    
    cart = cart.filter(item => item.id !== id);
    
    localStorage.setItem('cart', JSON.stringify(cart));
}

// Función para vaciar el carrito
function clearCart() {
    localStorage.removeItem('cart');
}

// Función para actualizar el contador del carrito
function updateCartCounter() {
    const cartCounter = document.querySelector('.cart-counter');
    if (!cartCounter) return;
    
    const cartItems = getCartItems();
    const itemCount = cartItems.reduce((total, item) => total + item.cantidad, 0);
    
    cartCounter.textContent = itemCount;
    
    // Mostrar u ocultar el contador según si hay productos
    if (itemCount > 0) {
        cartCounter.style.display = 'block';
    } else {
        cartCounter.style.display = 'none';
    }
}