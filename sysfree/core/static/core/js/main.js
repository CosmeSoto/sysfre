// Funcionalidad para mensajes temporales
document.addEventListener('DOMContentLoaded', function() {
    // Ocultar mensajes después de 5 segundos
    const messages = document.querySelectorAll('.message');
    if (messages.length > 0) {
        setTimeout(function() {
            messages.forEach(function(message) {
                message.style.opacity = '0';
                message.style.transition = 'opacity 0.5s ease';
                setTimeout(function() {
                    message.style.display = 'none';
                }, 500);
            });
        }, 5000);
    }
    
    // Inicializar datepickers si existen
    const datepickers = document.querySelectorAll('input[type="date"]');
    if (datepickers.length > 0) {
        // Si se implementa un datepicker personalizado, aquí iría su inicialización
    }
    
    // Inicializar selectores personalizados si existen
    const selects = document.querySelectorAll('select');
    if (selects.length > 0) {
        // Si se implementa un selector personalizado, aquí iría su inicialización
    }
});