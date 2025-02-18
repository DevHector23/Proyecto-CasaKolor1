const signUpButton = document.getElementById('signUp');
const signInButton = document.getElementById('signIn');
const container = document.getElementById('container');

signUpButton.addEventListener('click', () => {
    container.classList.add("right-panel-active");
});

signInButton.addEventListener('click', () => {
    container.classList.remove("right-panel-active");
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
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'auth-error-container';
                    const errorMessage = document.createElement('p');
                    errorMessage.className = 'auth-error-text';
                    errorMessage.textContent = 'Este campo es requerido';
                    errorDiv.appendChild(errorMessage);
                    
                    // Remover mensaje de error anterior si existe
                    const existingError = input.nextElementSibling;
                    if (existingError && existingError.className === 'auth-error-container') {
                        existingError.remove();
                    }
                    
                    input.insertAdjacentElement('afterend', errorDiv);
                }
            });
            
            if (!isValid) {
                e.preventDefault();
            }
        });
    });
});