document.addEventListener("DOMContentLoaded", function () {
    // Login success message
    if ("{{ request.session.login_success }}") {
        alert("¡Has iniciado sesión correctamente!");  // Mostrar mensaje
        fetch("{% url 'clear_login_success' %}", { 
            method: "POST", 
            headers: { "X-CSRFToken": "{{ csrf_token }}" } 
        });
    }

    // Product search functionality
    const searchInput = document.getElementById('productSearch');
    const productItems = document.querySelectorAll('.product-item');

    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase().trim();

        productItems.forEach(item => {
            const name = item.getAttribute('data-name');
            const description = item.getAttribute('data-description');

            if (name.includes(searchTerm) || description.includes(searchTerm)) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    });
});