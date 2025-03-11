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

    // Verificar si el elemento existe antes de agregar el event listener
    const confirmarCompraBtn = document.getElementById('confirmarCompra');
    if (confirmarCompraBtn) {
        confirmarCompraBtn.addEventListener('click', function () {
            const nombre = document.getElementById('nombre').value;
            const correo = document.getElementById('correo').value;
            const telefono = document.getElementById('telefono').value;
            const facturaInput = document.getElementById('factura');

            // Validación de campos
            if (!nombre || !correo || !telefono) {
                alert('Por favor, complete todos los campos: nombre, correo y teléfono.');
                return;
            }

            // Validación de correo electrónico
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(correo)) {
                alert('Por favor, ingrese un correo electrónico válido.');
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
            
            const transactionToken = Date.now().toString() + Math.random().toString(36).substring(2, 15);
            formData.append('transaction_token', transactionToken);

            const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
            if (csrfTokenElement) {
                formData.append('csrfmiddlewaretoken', csrfTokenElement.value);
            }

            // Deshabilitar el botón para evitar múltiples envíos
            confirmarCompraBtn.disabled = true;
            confirmarCompraBtn.textContent = 'Procesando...';

            // Mostrar un indicador de carga
            const loadingIndicator = document.createElement('div');
            loadingIndicator.id = 'loading-indicator';
            loadingIndicator.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Cargando...</span></div>';
            loadingIndicator.style.position = 'fixed';
            loadingIndicator.style.top = '50%';
            loadingIndicator.style.left = '50%';
            loadingIndicator.style.transform = 'translate(-50%, -50%)';
            loadingIndicator.style.zIndex = '9999';
            document.body.appendChild(loadingIndicator);

            fetch('/finalizar-compra/', {
                method: 'POST',
                body: formData,
                // Evitar que se cierre la conexión antes de recibir respuesta completa
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Error de servidor: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                // Eliminar el indicador de carga
                document.body.removeChild(loadingIndicator);
                
                if (data.success) {
                    // Vaciar el carrito y restablecer el contador
                    cart.length = 0;
                    localStorage.removeItem('cart');
                    localStorage.setItem('cartCount', 0);
                    
                    // Mostrar mensaje de éxito
                    alert('¡Compra realizada con éxito!');
                    
                    // Esperar un momento antes de redirigir para que el usuario vea el mensaje
                    setTimeout(() => {
                        // Usar ruta absoluta con barra al final para evitar problemas de redirección
                        window.location.href = '/productos/';
                    }, 1500);
                } else {
                    confirmarCompraBtn.disabled = false;
                    confirmarCompraBtn.textContent = 'Confirmar Compra';
                    
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
                
                // Eliminar el indicador de carga si existe
                const loadingElement = document.getElementById('loading-indicator');
                if (loadingElement) {
                    document.body.removeChild(loadingElement);
                }
                
                confirmarCompraBtn.disabled = false;
                confirmarCompraBtn.textContent = 'Confirmar Compra';
                alert('Error al procesar la compra. Por favor, inténtelo de nuevo más tarde.');
            });
        });
    }

    renderCart();
});