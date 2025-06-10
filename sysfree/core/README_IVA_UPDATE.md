# Actualización del Sistema de IVA

Este documento describe los cambios realizados para implementar un sistema global de IVA en SysFree, eliminando código redundante y centralizando la gestión del IVA.

## Cambios Realizados

1. **Eliminación del modelo Impuesto en fiscal**
   - Se eliminó completamente el modelo Impuesto
   - Se actualizaron todas las referencias en la API

2. **Actualización del modelo ConfiguracionSistema**
   - Se eliminó el campo `IVA_PORCENTAJE`
   - Se agregó un campo `tipo_iva_default` que referencia al modelo `TipoIVA`
   - Se crearon migraciones para estos cambios

3. **Creación del servicio IVAService**
   - Proporciona métodos para acceder a los tipos de IVA
   - Implementa caché para mejorar el rendimiento
   - Ofrece métodos para calcular el IVA

4. **Actualización del servicio ConfiguracionService**
   - Se mejoró para utilizar el servicio IVAService
   - Se eliminaron referencias al campo `IVA_PORCENTAJE`

5. **Actualización de modelos que utilizan IVA**
   - Se modificó el modelo `Producto` para usar `TipoIVA`
   - Se actualizó el modelo `DetalleVenta` para calcular el IVA usando el servicio
   - Se actualizó el servicio `VentaService` para usar el servicio IVA

## Migraciones

Se crearon las siguientes migraciones:

1. `fiscal/migrations/0002_remove_impuesto.py`: Elimina el modelo Impuesto
2. `core/migrations/0003_configuracionsistema_tipo_iva_default_remove_iva_porcentaje.py`: Agrega el campo tipo_iva_default y elimina IVA_PORCENTAJE
3. `core/migrations/0004_sincronizar_configuracion_iva.py`: Sincroniza la configuración con el tipo de IVA predeterminado

## Cómo Usar el Nuevo Sistema

Para obtener el tipo de IVA predeterminado:

```python
from core.services import IVAService

# Obtener el tipo de IVA predeterminado
iva_default = IVAService.get_default()

# Calcular IVA para un monto
base_imponible = Decimal('100.00')
monto_iva, total = IVAService.calcular_iva(base_imponible)
```

Para obtener la configuración del sistema:

```python
from core.services import ConfiguracionService

# Obtener la configuración del sistema
config = ConfiguracionService.get_configuracion()

# Obtener el tipo de IVA predeterminado desde la configuración
tipo_iva = ConfiguracionService.get_iva_default()

# Obtener el porcentaje de IVA predeterminado
porcentaje = ConfiguracionService.get_iva_porcentaje()
```