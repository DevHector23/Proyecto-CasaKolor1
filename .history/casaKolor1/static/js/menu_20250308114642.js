document.getElementById("toggle-search").addEventListener("click", function () {
    let searchInput = document.getElementById("search-input");
    
    // Modificar el tamaño de la barra de búsqueda
    searchInput.style.width = "150px";   // Ajusta el ancho deseado
    searchInput.style.height = "10px";   // Ajusta la altura deseada

    if (window.innerWidth <= 768) {
        // En móviles: mostramos la barra sin animaciones y le cambiamos el fondo para que se vea
        searchInput.style.backgroundColor = "white"; // Color de fondo para móviles (por ejemplo, dorado)
        searchInput.style.display = "block";
        searchInput.style.opacity = "1"; // Forzamos la visibilidad
        searchInput.focus();
    } else {
        // En pantallas grandes: usamos la animación y restablecemos el fondo por defecto
        searchInput.style.backgroundColor = "#ffffff"; // Fondo blanco (o el color que prefieras)
        if (searchInput.style.opacity === "0" || searchInput.style.opacity === "") {
            searchInput.style.display = "block";
            setTimeout(() => {
                searchInput.style.opacity = "1";
            }, 10);
            searchInput.focus();
        } else {
            searchInput.style.opacity = "0";
            setTimeout(() => {
                searchInput.style.display = "none";
            }, 300);
        }
    }
});
