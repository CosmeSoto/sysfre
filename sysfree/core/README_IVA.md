# Implementación del Sistema Global de IVA

Este documento describe la implementación del sistema global de IVA en SysFree, que permite manejar los tipos de IVA de forma centralizada en toda la aplicación.

## Componentes Implementados

1. **Servicio de IVA (IVAService)**
   - Ubicado en `/sysfree/core/services/iva_service.py`
   - Proporciona métodos para:
     - Obtener el tipo de IVA predeterminado
     - Obtener tipos de IVA por código o porcentaje
     - Calcular montos de IVA
     - Gestionar caché para mejor rendimiento

2. **Utilidades de IVA**
   - Ubicadas en `/sysfree/core/utils/iva_utils.py`
   - Funciones helper para simplificar el uso del servicio

3. **Template Tags**
   - Ubicados en `/sysfree/core/templatetags/iva_tags.py`
   - Permiten usar el servicio de IVA directamente en las plantillas

4. **Context Processor**
   - Ubicado en `/sysfree/core/context_processors.py`
   - Añade información de IVA a todas las plantillas automáticamente

5. **Signals**
   - Actualizados en `/sysfree/core/signals.py`
   - Invalidan la caché cuando se modifican los tipos de IVA

## Cambios en los Modelos

### Producto (inventario)
- Se agregó un campo `tipo_iva` que referencia al modelo `TipoIVA`
- Se modificó el método `save()` para sincronizar el campo `iva` con el porcentaje del `tipo_iva`
- Se crearon migraciones para agregar el campo y sincronizar los datos existentes

### DetalleVenta (ventas)
- Se modificó el método `save()` para usar el servicio `IVAService` en el cálculo del IVA

## Cambios en los Servicios

### VentaService (ventas)
- Se modificó el método `crear_venta()` para usar el servicio `IVAService` en el cálculo del IVA

## Cómo Usar el Servicio de IVA

### En modelos y servicios:
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

### En plantillas:
```html
{% load iva_tags %}

<!-- Filtros -->
<p>Precio sin IVA: $100.00</p>
<p>Precio con IVA: ${{ 100.00|aplicar_iva }}</p>
<p>Monto de IVA: ${{ 100.00|monto_iva }}</p>

<!-- Variables disponibles en todas las plantillas -->
<p>IVA predeterminado: {{ iva_default.nombre }} ({{ iva_default.porcentaje }}%)</p>
```

## Migraciones Necesarias

Para aplicar estos cambios, es necesario ejecutar las migraciones:

```bash
python manage.py migrate
```

Esto aplicará las migraciones `0002_producto_tipo_iva.py` y `0003_sincronizar_tipo_iva.py` que agregan el campo `tipo_iva` al modelo `Producto` y sincronizan los datos existentes.