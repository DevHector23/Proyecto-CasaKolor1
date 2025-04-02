document.addEventListener('DOMContentLoaded', function() {
    // Elementos principales
    const container = document.getElementById('container');
    const loginSection = document.getElementById('login-section');
    const registerSection = document.getElementById('register-section');
    const switchToRegister = document.getElementById('switchToRegister');
    const switchToLogin = document.getElementById('switchToLogin');
    const signInBtn = document.getElementById('signIn');
    const signUpBtn = document.getElementById('signUp');
    
    // Verificar si estamos en modo registro por errores
    const registerErrors = document.querySelector('.auth-signup-section .auth-error-container');
    const mode = "{{ mode }}";
    
    // Función para verificar el tamaño de pantalla
    function isMobile() {
        return window.innerWidth <= 768;
    }
    
    // Inicialización basada en errores o modo
    if (registerErrors || mode === 'register') {
        container.classList.add("right-panel-active", "register-mode");
        
        if (isMobile()) {
            loginSection.style.display = 'none';
            registerSection.style.display = 'block';
        }
    }
    
    // Manejo de switches en móvil
    if (switchToRegister && switchToLogin) {
        switchToRegister.addEventListener('click', function() {
            loginSection.style.display = 'none';
            registerSection.style.display = 'block';
            container.classList.add('register-mode');
            
            // Scroll al formulario de registro
            registerSection.scrollIntoView({ behavior: 'smooth' });
        });
        
        switchToLogin.addEventListener('click', function() {
            registerSection.style.display = 'none';
            loginSection.style.display = 'block';
            container.classList.remove('register-mode');
            
            // Scroll al formulario de login
            loginSection.scrollIntoView({ behavior: 'smooth' });
        });
    }
    
    // Manejo de switches en desktop
    if (signInBtn && signUpBtn) {
        signInBtn.addEventListener('click', function() {
            if (!container.classList.contains("right-panel-active")) return;
            container.classList.remove("right-panel-active");
        });
        
        signUpBtn.addEventListener('click', function() {
            if (container.classList.contains("right-panel-active")) return;
            container.classList.add("right-panel-active");
        });
    }
    
    // Manejo del CSRF Token
    function areCookiesEnabled() {
        try {
            document.cookie = "testcookie=1";
            var cookieEnabled = document.cookie.indexOf("testcookie") !== -1;
            document.cookie = "testcookie=1; expires=Thu, 01 Jan 1970 00:00:00 UTC";
            return cookieEnabled;
        } catch (e) {
            return false;
        }
    }
    
    // Mostrar advertencia si las cookies están deshabilitadas
    if (!areCookiesEnabled()) {
        const warningDiv = document.createElement('div');
        warningDiv.style.backgroundColor = '#ffdddd';
        warningDiv.style.padding = '10px';
        warningDiv.style.margin = '10px 0';
        warningDiv.style.borderRadius = '5px';
        warningDiv.style.textAlign = 'center';
        warningDiv.textContent = 'Las cookies parecen estar deshabilitadas. Por favor, habilítalas para poder iniciar sesión correctamente.';
        document.body.insertBefore(warningDiv, document.body.firstChild);
    }
    
    // Refrescar el token CSRF antes de enviar el formulario
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]');
            if (!csrfToken || csrfToken.value.length < 10) {
                e.preventDefault();
                location.reload();
                return false;
            }
            
            // Mostrar loader durante el envío
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';
                submitBtn.disabled = true;
            }
        });
    });
    
    // Manejo responsive al cambiar tamaño de pantalla
    window.addEventListener('resize', function() {
        if (isMobile()) {
            // En móvil, asegurarse que solo se muestra un formulario a la vez
            if (container.classList.contains('register-mode')) {
                loginSection.style.display = 'none';
                registerSection.style.display = 'block';
            } else {
                loginSection.style.display = 'block';
                registerSection.style.display = 'none';
            }
        } else {
            // En desktop, mostrar ambos formularios (controlado por right-panel-active)
            loginSection.style.display = 'block';
            registerSection.style.display = 'block';
        }
    });
    
    // Enfocar el primer campo con error si existe
    const firstErrorField = document.querySelector('.auth-error-container');
    if (firstErrorField) {
        const inputWithError = firstErrorField.closest('.auth-input-group')?.querySelector('input');
        if (inputWithError) {
            setTimeout(() => {
                inputWithError.focus();
            }, 300);
        }
    }
});