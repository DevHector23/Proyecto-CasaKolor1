document.addEventListener('DOMContentLoaded', function() {
    // Variables
    const slides = document.querySelectorAll('.carousel-slide');
    const prevBtn = document.querySelector('.carousel-control.prev');
    const nextBtn = document.querySelector('.carousel-control.next');
    const indicators = document.querySelectorAll('.indicator');
    
    let currentSlide = 0;
    let slideInterval;
    
    // Configurar los fondos de las diapositivas y precargar imágenes
    function preloadImages() {
        let imagesLoaded = 0;
        const totalImages = slides.length;
        
        slides.forEach(slide => {
            const bgImage = slide.getAttribute('data-bg');
            const img = new Image();
            
            img.onload = function() {
                slide.style.backgroundImage = `url('${bgImage}')`;
                imagesLoaded++;
                
                // Cuando todas las imágenes estén cargadas, iniciamos el carrusel
                if (imagesLoaded === totalImages) {
                    startCarousel();
                }
            };
            
            img.onerror = function() {
                console.error(`Error al cargar la imagen: ${bgImage}`);
                imagesLoaded++;
                
                // Si hay error, usamos un color de fondo como respaldo
                slide.style.backgroundColor = '#333';
                
                if (imagesLoaded === totalImages) {
                    startCarousel();
                }
            };
            
            img.src = bgImage;
        });
    }
    
    // Iniciar el carrusel después de cargar las imágenes
    function startCarousel() {
        // Mostrar la primera diapositiva
        showSlide(0);
        
        // Iniciar el intervalo de cambio automático
        slideInterval = setInterval(nextSlide, 3500);
    }
    
    // Funciones
    function showSlide(index) {
        // Eliminar clase active de todos los slides e indicadores
        slides.forEach(slide => slide.classList.remove('active'));
        indicators.forEach(indicator => indicator.classList.remove('active'));
        
        // Activar el slide actual
        slides[index].classList.add('active');
        indicators[index].classList.add('active');
        
        // Actualizar índice actual
        currentSlide = index;
    }
    
    function nextSlide() {
        let newIndex = currentSlide + 1;
        if (newIndex >= slides.length) {
            newIndex = 0;
        }
        showSlide(newIndex);
    }
    
    function prevSlide() {
        let newIndex = currentSlide - 1;
        if (newIndex < 0) {
            newIndex = slides.length - 1;
        }
        showSlide(newIndex);
    }
    
    function resetInterval() {
        clearInterval(slideInterval);
        slideInterval = setInterval(nextSlide, 3500);
    }
    
    // Event Listeners
    nextBtn.addEventListener('click', function() {
        nextSlide();
        resetInterval();
    });
    
    prevBtn.addEventListener('click', function() {
        prevSlide();
        resetInterval();
    });
    
    // Agregar evento a los indicadores
    indicators.forEach((indicator, index) => {
        indicator.addEventListener('click', function() {
            showSlide(index);
            resetInterval();
        });
    });
    
    // Pausar el carrusel cuando el usuario pasa el mouse por encima
    document.querySelector('.hero-carousel').addEventListener('mouseenter', function() {
        clearInterval(slideInterval);
    });
    
    // Reanudar el carrusel cuando el mouse sale
    document.querySelector('.hero-carousel').addEventListener('mouseleave', function() {
        slideInterval = setInterval(nextSlide, 3500);
    });
    
    // Iniciar la precarga de imágenes
    preloadImages();
});