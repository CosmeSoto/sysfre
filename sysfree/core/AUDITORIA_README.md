# Sistema de Auditoría Mejorado - SysFree

## Descripción

El sistema de auditoría mejorado de SysFree proporciona un registro detallado y profesional de todas las actividades importantes del sistema, incluyendo:

- **Auditoría automática** de modelos mediante Django Signals
- **Registro de autenticación** (login, logout, fallos)
- **Seguimiento de cambios** con datos anteriores y actuales
- **Información contextual** (IP, User-Agent, usuario)
- **Acciones estandarizadas** con constantes predefinidas

## Archivos Creados/Modificados

### Nuevos Archivos
- `core/constants.py` - Constantes para acciones, niveles y tipos
- `core/services/auditoria_service.py` - Servicio avanzado de auditoría
- `core/mixins/auditoria_mixins.py` - Mixins para vistas y señales de auth
- `core/examples/ejemplo_uso_auditoria.py` - Ejemplos de uso

### Archivos Modificados
- `core/models/auditoria.py` - Ya tenía los campos `datos_anteriores` y `user_agent`
- `core/services/log_service.py` - Ya estaba actualizado
- `core/middleware.py` - Mejorado para incluir request completo
- `core/signals.py` - Sistema de auditoría automática
- `core/apps.py` - Importa las señales automáticamente

## Características Principales

### 1. Auditoría Automática de Modelos

Los modelos en `AUDITED_MODELS` se auditan automáticamente:

```python
# En core/signals.py
AUDITED_MODELS = [TipoIVA]  # Añade más modelos aquí
```

**Qué se registra automáticamente:**
- ✅ Creación de registros
- ✅ Actualización de registros (solo si hay cambios reales)
- ✅ Eliminación de registros
- ✅ Datos anteriores vs nuevos datos
- ✅ Usuario que realizó la acción
- ✅ IP y User-Agent del cliente

### 2. Auditoría de Autenticación

Se registra automáticamente:
- ✅ Login exitoso
- ✅ Login fallido
- ✅ Logout
- ✅ Cambios de contraseña

### 3. Servicios Especializados

#### AuditoriaService
```python
from core.services.auditoria_service import AuditoriaService

# Registrar venta
AuditoriaService.venta_creada(venta, detalles)

# Registrar cambio de stock
AuditoriaService.stock_actualizado(producto, cantidad_anterior, cantidad_nueva, motivo)

# Registrar acceso denegado
AuditoriaService.acceso_denegado(recurso, motivo)
```

## Cómo Usar

### 1. Añadir Modelos a Auditoría Automática

Edita `core/signals.py`:

```python
AUDITED_MODELS = [
    TipoIVA,
    # Añade tus modelos aquí:
    # Producto,
    # Cliente,
    # Venta,
    # Usuario,
]
```

### 2. Usar en Vistas

```python
from core.mixins.auditoria_mixins import AuditoriaMixin
from core.services.auditoria_service import AuditoriaService

class MiVista(AuditoriaMixin, CreateView):
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Registrar acción personalizada
        self.registrar_accion(
            accion="PRODUCTO_CREADO",
            descripcion=f"Producto {self.object.nombre} creado"
        )
        
        return response
```

### 3. Usar en Servicios

```python
def procesar_venta(venta_data):
    # Tu lógica de negocio
    venta = crear_venta(venta_data)
    
    # Auditoría
    AuditoriaService.venta_creada(venta)
    
    return venta
```

### 4. Decorador para Funciones

```python
from core.examples.ejemplo_uso_auditoria import auditar_accion

@auditar_accion(
    accion="BACKUP_CREADO",
    descripcion_template="Backup creado en {ruta}"
)
def crear_backup(ruta):
    # Tu lógica aquí
    return archivo_backup
```

## Información Registrada

Cada entrada de auditoría incluye:

| Campo | Descripción |
|-------|-------------|
| `usuario` | Usuario que realizó la acción |
| `fecha` | Timestamp de la acción |
| `ip` | Dirección IP del cliente |
| `user_agent` | Información del navegador/cliente |
| `nivel` | info, warning, error, critical |
| `tipo` | sistema, usuario, seguridad, negocio |
| `accion` | Código de acción estandarizado |
| `descripcion` | Descripción legible de la acción |
| `modelo` | Nombre del modelo afectado |
| `objeto_id` | ID del objeto afectado |
| `datos` | Datos actuales del objeto |
| `datos_anteriores` | Estado anterior (para actualizaciones) |

## Acciones Estandarizadas

Las constantes en `core/constants.py` incluyen:

### Autenticación
- `LOGIN_EXITOSO`
- `LOGIN_FALLIDO`
- `LOGOUT`
- `CAMBIO_PASSWORD`

### Negocio
- `VENTA_CREADA`
- `VENTA_ANULADA`
- `STOCK_ACTUALIZADO`
- `PRODUCTO_CREADO`
- `CLIENTE_CREADO`

### Sistema
- `CONFIGURACION_ACTUALIZADA`
- `BACKUP_CREADO`
- `SISTEMA_ACTUALIZADO`

### Seguridad
- `ACCESO_DENEGADO`
- `SESION_EXPIRADA`

## Consultar Logs

### En el Admin de Django
Los logs aparecen en el admin como "Logs de actividad"

### Programáticamente
```python
from core.models.auditoria import LogActividad

# Logs de un usuario específico
logs_usuario = LogActividad.objects.filter(usuario=usuario)

# Logs de un tipo específico
logs_ventas = LogActividad.objects.filter(tipo='negocio', accion__contains='VENTA')

# Logs con errores
logs_errores = LogActividad.objects.filter(nivel='error')

# Logs de los últimos 7 días
from datetime import datetime, timedelta
hace_7_dias = datetime.now() - timedelta(days=7)
logs_recientes = LogActividad.objects.filter(fecha__gte=hace_7_dias)
```

## Próximos Pasos Recomendados

1. **Añadir más modelos** a `AUDITED_MODELS` según tus necesidades
2. **Integrar en vistas existentes** usando `AuditoriaMixin`
3. **Crear reportes de auditoría** para análisis
4. **Configurar alertas** para eventos críticos
5. **Implementar retención de logs** (limpieza automática)

## Consideraciones de Rendimiento

- La auditoría automática añade consultas extra (1 por actualización)
- Para alto volumen, considera auditar solo modelos críticos
- Los logs crecen rápidamente - implementa limpieza periódica

## Seguridad

- Los logs incluyen información sensible - protege el acceso
- Los datos anteriores pueden contener información confidencial
- Considera encriptar campos sensibles en `datos` y `datos_anteriores`