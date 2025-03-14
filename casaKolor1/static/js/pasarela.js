document.addEventListener('DOMContentLoaded', () => {
    // Elementos del DOM
    const continueToPaymentBtn = document.getElementById('continue-to-payment');
    const backToInfoBtn = document.getElementById('back-to-info');
    const confirmarCompraBtn = document.getElementById('confirmarCompra');
    const loadingOverlay = document.getElementById('loading-overlay');
    const orderItems = document.getElementById('order-items');
    const orderSubtotal = document.getElementById('order-subtotal');
    const orderTotal = document.getElementById('order-total');
    const paymentAmount = document.getElementById('payment-amount');
    
    // Secciones del formulario
    const step1 = document.getElementById('step-1');
    const step2 = document.getElementById('step-2');
    const step3 = document.getElementById('step-3');
    const contactInfoSection = document.getElementById('contact-info-section');
    const paymentSection = document.getElementById('payment-section');
    const successSection = document.getElementById('success-section');

    // Variables
    let cart = JSON.parse(localStorage.getItem('cart')) || [];
    let isSubmitting = false;

    // Funciones
    function renderOrderSummary() {
        if (orderItems) {
            orderItems.innerHTML = '';
            let total = 0;

            if (cart.length === 0) {
                orderItems.innerHTML = '<div class="empty-cart-message">El carrito está vacío</div>';
                orderSubtotal.textContent = '$0';
                orderTotal.textContent = '$0';
                paymentAmount.textContent = '0';
                return;
            }

            cart.forEach(item => {
                const subtotal = item.precio * item.cantidad;
                total += subtotal;

                const itemElement = document.createElement('div');
                itemElement.className = 'order-item';
                itemElement.innerHTML = `
                    <div class="order-item-details">
                        <div class="order-item-name">${item.nombre}</div>
                        <div class="order-item-price">$${item.precio.toLocaleString('es')} x ${item.cantidad}</div>
                    </div>
                    <div class="order-item-total">$${Math.floor(subtotal).toLocaleString('es')}</div>
                `;
                orderItems.appendChild(itemElement);
            });

            // Actualizar totales
            orderSubtotal.textContent = `$${Math.floor(total).toLocaleString('es')}`;
            orderTotal.textContent = `$${Math.floor(total).toLocaleString('es')}`;
            paymentAmount.textContent = `${Math.floor(total).toLocaleString('es')}`;
        }
    }

    function showSection(sectionToShow) {
        // Ocultar todas las secciones
        contactInfoSection.classList.remove('show');
        paymentSection.classList.remove('show');
        successSection.classList.remove('show');
        
        // Mostrar la sección solicitada
        sectionToShow.classList.add('show');
    }

    function updateSteps(activeStep) {
        // Reiniciar estados
        step1.classList.remove('active', 'completed');
        step2.classList.remove('active', 'completed');
        step3.classList.remove('active', 'completed');
        
        // Actualizar según el paso activo
        if (activeStep === 1) {
            step1.classList.add('active');
        } else if (activeStep === 2) {
            step1.classList.add('completed');
            step2.classList.add('active');
        } else if (activeStep === 3) {
            step1.classList.add('completed');
            step2.classList.add('completed');
            step3.classList.add('active');
        }
    }

    function validateContactInfo() {
        const nombre = document.getElementById('nombre');
        const correo = document.getElementById('correo');
        const telefono = document.getElementById('telefono');
        let isValid = true;

        // Validar nombre
        if (!nombre.value.trim()) {
            nombre.classList.add('is-invalid');
            isValid = false;
        } else {
            nombre.classList.remove('is-invalid');
        }

        // Validar correo
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!correo.value.trim() || !emailRegex.test(correo.value)) {
            correo.classList.add('is-invalid');
            isValid = false;
        } else {
            correo.classList.remove('is-invalid');
        }

        // Validar teléfono
        if (!telefono.value.trim()) {
            telefono.classList.add('is-invalid');
            isValid = false;
        } else {
            telefono.classList.remove('is-invalid');
        }

        return isValid;
    }

    function validatePaymentInfo() {
        const facturaInput = document.getElementById('factura');
        
        if (!facturaInput || !facturaInput.files || facturaInput.files.length === 0) {
            facturaInput.classList.add('is-invalid');
            return false;
        } else {
            facturaInput.classList.remove('is-invalid');
            return true;
        }
    }

    function procesarCompra() {
        if (isSubmitting) return;
        
        if (!validatePaymentInfo()) {
            return;
        }
        
        const nombre = document.getElementById('nombre').value;
        const correo = document.getElementById('correo').value;
        const telefono = document.getElementById('telefono').value;
        const facturaInput = document.getElementById('factura');
        const total = cart.reduce((sum, item) => sum + (item.precio * item.cantidad), 0);

        const formData = new FormData();
        formData.append('nombre', nombre);
        formData.append('correo', correo);
        formData.append('telefono', telefono);
        formData.append('total', total);
        formData.append('items', JSON.stringify(cart));
        formData.append('comprobante', facturaInput.files[0]);
        
        // Generar un token único para esta transacción
        const transactionToken = Date.now().toString() + Math.random().toString(36).substring(2, 15);
        formData.append('transaction_token', transactionToken);

        const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfTokenElement) {
            formData.append('csrfmiddlewaretoken', csrfTokenElement.value);
        }

        // Activar la bandera de envío
        isSubmitting = true;
        
        // Deshabilitar el botón para evitar múltiples envíos
        confirmarCompraBtn.disabled = true;
        
        // Mostrar el loader
        loadingOverlay.style.display = 'flex';

        // Establecer un tiempo de espera máximo para la solicitud
        const timeoutDuration = 30000; // 30 segundos
        let timeoutId = setTimeout(() => {
            loadingOverlay.style.display = 'none';
            confirmarCompraBtn.disabled = false;
            isSubmitting = false;
            alert('La solicitud está tomando demasiado tiempo. Por favor, intente nuevamente más tarde.');
        }, timeoutDuration);

        fetch('/finalizar-compra/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            clearTimeout(timeoutId); // Limpiar el timeout si la respuesta llega a tiempo
            
            // Si el status no es OK, convertir a JSON antes
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.message || 'Error en el servidor');
                });
            }
            return response.json();
        })
        .then(data => {
            // Ocultar el loader
            loadingOverlay.style.display = 'none';
            
            if (data.success) {
                // Actualizar número de pedido en la sección de éxito
                document.getElementById('order-number').textContent = `#${data.pedido_id}`;
                
                // Mostrar la sección de éxito
                showSection(successSection);
                updateSteps(3);
                
                // Limpiar carrito
                localStorage.removeItem('cart');
                cart = [];
                
                // Actualizar el resumen
                renderOrderSummary();
            } else {
                alert(data.message || 'Error al procesar la compra');
                confirmarCompraBtn.disabled = false;
                isSubmitting = false;
            }
        })
        .catch(error => {
            loadingOverlay.style.display = 'none';
            confirmarCompraBtn.disabled = false;
            isSubmitting = false;
            alert('Error: ' + error.message);
            console.error('Error:', error);
        });
    }

    // Event Listeners
    if (continueToPaymentBtn) {
        continueToPaymentBtn.addEventListener('click', () => {
            if (validateContactInfo()) {
                showSection(paymentSection);
                updateSteps(2);
            }
        });
    }

    if (backToInfoBtn) {
        backToInfoBtn.addEventListener('click', () => {
            showSection(contactInfoSection);
            updateSteps(1);
        });
    }

    if (confirmarCompraBtn) {
        confirmarCompraBtn.addEventListener('click', procesarCompra);
    }

    // Inicializar
    renderOrderSummary();
    showSection(contactInfoSection);
    updateSteps(1);
});