/**
 * JavaScript para mejorar la experiencia en dispositivos móviles
 */

document.addEventListener('DOMContentLoaded', function() {
    // Botón para volver arriba
    const backToTopButton = document.createElement('button');
    backToTopButton.className = 'back-to-top';
    backToTopButton.innerHTML = '<i class="fas fa-arrow-up"></i>';
    backToTopButton.setAttribute('aria-label', 'Volver arriba');
    document.body.appendChild(backToTopButton);
    
    // Mostrar/ocultar botón según el scroll
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTopButton.classList.add('visible');
        } else {
            backToTopButton.classList.remove('visible');
        }
    });
    
    // Acción del botón
    backToTopButton.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    
    // Filtros móviles
    const filterToggle = document.getElementById('filter-toggle');
    const filterSidebar = document.getElementById('filter-sidebar');
    const filterOverlay = document.getElementById('filter-overlay');
    const closeFilter = document.getElementById('close-filter');
    
    if (filterToggle && filterSidebar && filterOverlay && closeFilter) {
        filterToggle.addEventListener('click', function() {
            filterSidebar.classList.add('open');
            filterOverlay.classList.add('open');
            document.body.classList.add('overflow-hidden');
        });
        
        function closeFilterSidebar() {
            filterSidebar.classList.remove('open');
            filterOverlay.classList.remove('open');
            document.body.classList.remove('overflow-hidden');
        }
        
        closeFilter.addEventListener('click', closeFilterSidebar);
        filterOverlay.addEventListener('click', closeFilterSidebar);
    }
    
    // Mejorar tablas responsivas
    const tables = document.querySelectorAll('table');
    tables.forEach(function(table) {
        const wrapper = document.createElement('div');
        wrapper.className = 'responsive-table';
        table.parentNode.insertBefore(wrapper, table);
        wrapper.appendChild(table);
    });
    
    // Mejorar experiencia de formularios en móviles
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(function(input) {
            // Evitar zoom en iOS al enfocar inputs
            if (input.type !== 'checkbox' && input.type !== 'radio') {
                input.style.fontSize = '16px';
            }
        });
    });
    
    // Detectar si es un dispositivo táctil
    const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    if (isTouchDevice) {
        document.body.classList.add('touch-device');
    }
});