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
        },
        // Establecer un tiempo de espera razonable
        timeout: 30000
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