# Core - Módulo Central de SysFree

Este módulo contiene la funcionalidad central del sistema SysFree, incluyendo:

- Gestión de usuarios
- Configuración del sistema
- Modelos base
- Servicios compartidos
- Utilidades comunes

## Servicio de IVA Global

El sistema implementa un servicio global para manejar los tipos de IVA en toda la aplicación, sin depender de configuraciones en settings.

### Uso del Servicio de IVA

Para utilizar el servicio de IVA en cualquier parte de la aplicación:

```python
from core.services import IVAService

# Obtener el IVA predeterminado
iva_default = IVAService.get_default()

# Calcular IVA para un monto
base_imponible = Decimal('100.00')
monto_iva, total = IVAService.calcular_iva(base_imponible)

# Obtener un IVA específico por código
iva_reducido = IVAService.get_by_codigo('REDUCIDO')

# Calcular IVA con un tipo específico
monto_iva, total = IVAService.calcular_iva(base_imponible, iva_reducido)
```

### Utilidades de IVA

También se proporcionan utilidades para simplificar el uso del IVA:

```python
from core.utils.iva_utils import aplicar_iva_default, get_iva_default_info

# Aplicar IVA predeterminado
monto_iva, total = aplicar_iva_default(Decimal('100.00'))

# Obtener información del IVA predeterminado
info = get_iva_default_info()
print(f"IVA: {info['nombre']} ({info['porcentaje']}%)")
```

### Template Tags

En las plantillas, puedes usar los siguientes tags:

```html
{% load iva_tags %}

<!-- Obtener el IVA predeterminado -->
{% get_iva_default as iva %}
<p>IVA predeterminado: {{ iva.nombre }} ({{ iva.porcentaje }}%)</p>

<!-- Calcular IVA -->
{% calcular_iva 100.00 as resultado_iva %}
<p>Monto IVA: {{ resultado_iva.0 }}</p>
<p>Total con IVA: {{ resultado_iva.1 }}</p>

<!-- Filtros -->
<p>Precio sin IVA: $100.00</p>
<p>Precio con IVA: ${{ 100.00|aplicar_iva }}</p>
<p>Monto de IVA: ${{ 100.00|monto_iva }}</p>
<p>Porcentaje de IVA: {{ porcentaje_iva_default }}</p>
```

### Context Processor

El sistema incluye un context processor que añade información sobre los tipos de IVA a todas las plantillas:

```html
<!-- Disponible en todas las plantillas -->
<p>IVA predeterminado: {{ iva_default.nombre }} ({{ iva_default.porcentaje }}%)</p>

<!-- Listar todos los tipos de IVA -->
<ul>
  {% for iva in tipos_iva %}
    <li>{{ iva.nombre }} ({{ iva.porcentaje }}%)</li>
  {% endfor %}
</ul>
```