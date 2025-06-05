// Funcionalidad para mensajes temporales
document.addEventListener('DOMContentLoaded', function() {
    // Ocultar mensajes después de 5 segundos
    const messages = document.querySelectorAll('.alert');
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

// Función para confirmar eliminación
function confirmarEliminacion(event, mensaje) {
    if (!confirm(mensaje || '¿Está seguro de que desea eliminar este elemento?')) {
        event.preventDefault();
        return false;
    }
    return true;
}

// Función para validar formularios
function validarFormulario(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;
    
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Función para formatear números como moneda
function formatoMoneda(valor) {
    return new Intl.NumberFormat('es-EC', {
        style: 'currency',
        currency: 'USD'
    }).format(valor);
}

// Función para calcular totales en formularios de venta
function calcularTotales() {
    const subtotalElement = document.getElementById('subtotal');
    const impuestosElement = document.getElementById('impuestos');
    const descuentoElement = document.getElementById('descuento');
    const totalElement = document.getElementById('total');
    
    if (!subtotalElement || !impuestosElement || !descuentoElement || !totalElement) return;
    
    const subtotal = parseFloat(subtotalElement.value) || 0;
    const impuestos = parseFloat(impuestosElement.value) || 0;
    const descuento = parseFloat(descuentoElement.value) || 0;
    
    const total = subtotal + impuestos - descuento;
    totalElement.value = total.toFixed(2);
    
    // Actualizar visualización si existe
    const totalDisplay = document.getElementById('total-display');
    if (totalDisplay) {
        totalDisplay.textContent = formatoMoneda(total);
    }
}