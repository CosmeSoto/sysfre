# API de SysFree

Esta API proporciona acceso a los datos del sistema SysFree a través de endpoints RESTful.

## Autenticación

Todos los endpoints requieren autenticación. La API soporta los siguientes métodos de autenticación:

- Autenticación básica
- Autenticación por sesión
- Autenticación por token (JWT)

## Endpoints principales

### Productos

- `GET /api/productos/` - Listar todos los productos
- `POST /api/productos/` - Crear un nuevo producto
- `GET /api/productos/{id}/` - Obtener detalles de un producto
- `PUT /api/productos/{id}/` - Actualizar un producto completo
- `PATCH /api/productos/{id}/` - Actualizar parcialmente un producto
- `DELETE /api/productos/{id}/` - Eliminar un producto

### Categorías

- `GET /api/categorias/` - Listar todas las categorías
- `POST /api/categorias/` - Crear una nueva categoría
- `GET /api/categorias/{id}/` - Obtener detalles de una categoría
- `PUT /api/categorias/{id}/` - Actualizar una categoría completa
- `PATCH /api/categorias/{id}/` - Actualizar parcialmente una categoría
- `DELETE /api/categorias/{id}/` - Eliminar una categoría

### Clientes

- `GET /api/clientes/` - Listar todos los clientes
- `POST /api/clientes/` - Crear un nuevo cliente
- `GET /api/clientes/{id}/` - Obtener detalles de un cliente
- `PUT /api/clientes/{id}/` - Actualizar un cliente completo
- `PATCH /api/clientes/{id}/` - Actualizar parcialmente un cliente
- `DELETE /api/clientes/{id}/` - Eliminar un cliente

### Ventas

- `GET /api/ventas/` - Listar todas las ventas
- `POST /api/ventas/` - Crear una nueva venta
- `GET /api/ventas/{id}/` - Obtener detalles de una venta
- `PUT /api/ventas/{id}/` - Actualizar una venta completa
- `PATCH /api/ventas/{id}/` - Actualizar parcialmente una venta
- `DELETE /api/ventas/{id}/` - Eliminar una venta

### Reparaciones

- `GET /api/reparaciones/` - Listar todas las reparaciones
- `POST /api/reparaciones/` - Crear una nueva reparación
- `GET /api/reparaciones/{id}/` - Obtener detalles de una reparación
- `PUT /api/reparaciones/{id}/` - Actualizar una reparación completa
- `PATCH /api/reparaciones/{id}/` - Actualizar parcialmente una reparación
- `DELETE /api/reparaciones/{id}/` - Eliminar una reparación

### Pedidos

- `GET /api/pedidos/` - Listar todos los pedidos
- `POST /api/pedidos/` - Crear un nuevo pedido
- `GET /api/pedidos/{id}/` - Obtener detalles de un pedido
- `PUT /api/pedidos/{id}/` - Actualizar un pedido completo
- `PATCH /api/pedidos/{id}/` - Actualizar parcialmente un pedido
- `DELETE /api/pedidos/{id}/` - Eliminar un pedido

## Endpoints personalizados

### Búsqueda de productos

- `GET /api/productos/buscar/?q=texto&categoria=id&precio_min=100&precio_max=200&disponible=1`

### Actualización de stock

- `POST /api/productos/{id}/stock/` - Con parámetros `cantidad` y `tipo` (entrada/salida)

### Actualización de estados

- `POST /api/ventas/{id}/estado/` - Con parámetro `estado`
- `POST /api/reparaciones/{id}/estado/` - Con parámetros `estado` y `descripcion`
- `POST /api/pedidos/{id}/estado/` - Con parámetro `estado`

### Estadísticas

- `GET /api/estadisticas/ventas/` - Estadísticas de ventas
- `GET /api/estadisticas/productos/` - Estadísticas de productos
- `GET /api/estadisticas/reparaciones/` - Estadísticas de reparaciones

## Paginación

Todos los endpoints que devuelven listas soportan paginación con los siguientes parámetros:

- `page` - Número de página
- `page_size` - Tamaño de página (máximo 100)

Ejemplo: `GET /api/productos/?page=2&page_size=20`

## Filtrado

La mayoría de los endpoints soportan filtrado por campos específicos:

Ejemplo: `GET /api/productos/?categoria=1&estado=activo`

## Ordenación

La mayoría de los endpoints soportan ordenación por campos específicos:

Ejemplo: `GET /api/productos/?ordering=precio_venta` o `GET /api/productos/?ordering=-precio_venta` (descendente)

## Búsqueda

La mayoría de los endpoints soportan búsqueda por texto:

Ejemplo: `GET /api/productos/?search=laptop`