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

    // Restaurar contador del carrito
    restoreCartCount(); 

    // Manejar clics en la página
    document.addEventListener('click', function (event) {
        // Agregar producto al carrito
        if (event.target.classList.contains('add-to-cart') || event.target.closest('.add-to-cart')) {
            const btn = event.target.closest('.add-to-cart');
            const card = btn ? btn.closest('.card') : null;
            
            if (!card) return;
            
            try {
                const id = btn.dataset.id;
                const nombre = card.querySelector('.card-title').textContent.trim();
                const descripcionElement = card.querySelector('.card-text');
                const descripcion = descripcionElement ? descripcionElement.textContent.trim() : '';
                const precioElement = card.querySelector('.card-text strong');
                
                if (!id || !nombre || !precioElement) {
                    console.error('Faltan datos del producto');
                    return;
                }
                
                const precioText = precioElement.textContent.replace('Precio: $', '').replace(/\./g, '').replace(/,/g, '.');
                const precio = parseFloat(precioText);
                
                if (isNaN(precio)) {
                    console.error('Precio no válido:', precioText);
                    return;
                }
                
                const imagen = card.querySelector('img') ? card.querySelector('img').src : '';

                const existingItem = cart.find(item => item.id === id);
                if (existingItem) {
                    existingItem.cantidad++;
                } else {
                    cart.push({ id, nombre, descripcion, precio, imagen, cantidad: 1 });
                }

                localStorage.setItem('cart', JSON.stringify(cart));
                renderCart();
                
                // Mostrar mensaje de confirmación
                const mensaje = document.createElement('div');
                mensaje.classList.add('alert', 'alert-success', 'position-fixed', 'top-0', 'end-0', 'm-3');
                mensaje.textContent = 'Producto agregado al carrito';
                mensaje.style.zIndex = '9999';
                document.body.appendChild(mensaje);
                setTimeout(() => mensaje.remove(), 2000);
            } catch (error) {
                console.error('Error al agregar producto:', error);
            }
        }

        // Eliminar producto del carrito
        if (event.target.closest('.remove-item')) {
            const button = event.target.closest('.remove-item');
            const id = button.dataset.id;
            const index = cart.findIndex(item => item.id === id);

            if (index !== -1) {
                cart.splice(index, 1);
                renderCart(); 
            }
        }

        // Vaciar carrito
        if (event.target.id === 'clear-cart-btn') {
            cart.length = 0;
            localStorage.removeItem('cart');
            localStorage.setItem('cartCount', 0); 
            renderCart();
        }

        // Mostrar modal de finalización de compra
        if (event.target.id === 'btnFinalizarCompra') {
            renderModalCart(); 
        }
    });

    // Manejar cambios en las cantidades
    document.addEventListener('change', function (event) {
        if (event.target.classList.contains('quantity-input')) {
            const id = event.target.dataset.id;
            const newQuantity = parseInt(event.target.value);
            const item = cart.find(item => item.id === id);

            if (item && newQuantity > 0) {
                item.cantidad = newQuantity;
                renderCart();
            } else if (newQuantity <= 0) {
                event.target.value = 1;
            }
        }
    });

    // Manejar envío del formulario de compra
    const confirmarCompraBtn = document.getElementById('confirmarCompra');
    if (confirmarCompraBtn) {
        confirmarCompraBtn.addEventListener('click', function () {
            // Validar que el carrito no esté vacío
            if (cart.length === 0) {
                alert('El carrito está vacío. Agregue productos antes de finalizar la compra.');
                return;
            }

            const nombre = document.getElementById('nombre').value.trim();
            const correo = document.getElementById('correo').value.trim();
            const telefono = document.getElementById('telefono').value.trim();
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

            // Función para intentar la petición con reintentos automáticos
            const fetchWithRetry = (url, options, retries = 3, delay = 1000) => {
                return new Promise((resolve, reject) => {
                    const attempt = () => {
                        fetch(url, options)
                            .then(response => {
                                if (response.ok) {
                                    resolve(response);
                                } else {
                                    throw new Error(`Error de servidor: ${response.status}`);
                                }
                            })
                            .catch(error => {
                                if (retries === 0) {
                                    reject(error);
                                    return;
                                }
                                
                                console.log(`Error en la petición, reintentando... (${retries} intentos restantes)`);
                                setTimeout(() => {
                                    attempt();
                                }, delay);
                                retries--;
                            });
                    };
                    attempt();
                });
            };

            // Usar ruta absoluta para evitar problemas de redirección
            fetchWithRetry('/finalizar-compra/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                // Eliminar el indicador de carga
                const loadingElement = document.getElementById('loading-indicator');
                if (loadingElement) {
                    document.body.removeChild(loadingElement);
                }
                
                if (data.success) {
                    // Vaciar el carrito y restablecer el contador
                    cart.length = 0;
                    localStorage.removeItem('cart');
                    localStorage.setItem('cartCount', 0);
                    
                    // Mostrar mensaje de éxito
                    alert('¡Compra realizada con éxito!');
                    
                    // Esperar un momento antes de redirigir para que el usuario vea el mensaje
                    setTimeout(() => {
                        // Usar ruta absoluta con barra al inicio para evitar problemas de redirección
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
                
                // Mensaje de error más amigable
                alert('Lo sentimos, ha ocurrido un problema al procesar la compra. Por favor, inténtelo de nuevo en unos momentos.');
            });
        });
    }

    // Renderizar el carrito al cargar la página
    renderCart();
});