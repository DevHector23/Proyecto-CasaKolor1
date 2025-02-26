const signUpButton = document.getElementById('signUp');
const signInButton = document.getElementById('signIn');
const container = document.getElementById('container');

signUpButton.addEventListener('click', () => {
    container.classList.add("right-panel-active");
});

signInButton.addEventListener('click', () => {
    container.classList.remove("right-panel-active");
});

// Cerrar mensajes de éxito automáticamente después de 5 segundos
document.addEventListener("DOMContentLoaded", function() {
    const messages = document.querySelectorAll(".alert");
    messages.forEach(message => {
        setTimeout(() => {
            message.style.display = "none";
        }, 5000);
    });
});

// Validación de formularios
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const inputs = form.querySelectorAll('input');
            let isValid = true;
            
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    showError(input, 'Este campo es requerido');
                }
            });

            const username = form.querySelector('input[name="username"]');
            if (username && username.value.length < 3) {
                isValid = false;
                showError(username, 'El nombre de usuario debe tener al menos 3 caracteres');
            }

            const password1 = form.querySelector('input[name="password1"]');
            const password2 = form.querySelector('input[name="password2"]');

            if (password1 && password2 && password1.value !== password2.value) {
                isValid = false;
                showError(password2, 'Las contraseñas no coinciden');
            }

            if (!isValid) {
                e.preventDefault();
            }
        });
    });

    function showError(input, message) {
        const existingError = input.nextElementSibling;
        if (existingError && existingError.className === 'auth-error-container') {
            existingError.remove();
        }

        const errorDiv = document.createElement('div');
        errorDiv.className = 'auth-error-container';
        const errorMessage = document.createElement('p');
        errorMessage.className = 'auth-error-text';
        errorMessage.textContent = message;
        errorDiv.appendChild(errorMessage);

        input.insertAdjacentElement('afterend', errorDiv);
    }
});
