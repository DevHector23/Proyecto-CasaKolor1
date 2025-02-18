document.getElementById("toggle-search").addEventListener("click", function () {
    let searchInput = document.getElementById("search-input");
    
    if (window.innerWidth <= 768) {
        // En móviles, muestra directamente sin animaciones
        searchInput.style.display = "block";
        searchInput.focus();
    } else {
        // En pantallas grandes, usa la animación
        if (searchInput.style.opacity === "0" || searchInput.style.opacity === "") {
            searchInput.style.display = "block";
            setTimeout(() => searchInput.style.opacity = "1", 10);
            searchInput.focus();
        } else {
            searchInput.style.opacity = "0";
            setTimeout(() => searchInput.style.display = "none", 300);
        }
    }
});
