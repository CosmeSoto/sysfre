# API Reference - SysFree

## Introducción

Esta documentación describe la API REST del sistema SysFree. La API permite interactuar con todos los módulos del sistema, incluyendo inventario, clientes, ventas, reparaciones, fiscal y e-commerce.

## Autenticación

La API utiliza autenticación basada en tokens JWT (JSON Web Tokens).

### Obtener Token

```
POST /api/token/
```

**Parámetros de solicitud:**

```json
{
  "email": "usuario@ejemplo.com",
  "password": "contraseña"
}
```

**Respuesta:**

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Refrescar Token

```
POST /api/token/refresh/
```

**Parámetros de solicitud:**

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Respuesta:**

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## Módulo Core

### Usuarios

#### Listar Usuarios

```
GET /api/usuarios/
```

**Parámetros de consulta:**
- `page`: Número de página
- `search`: Término de búsqueda

**Respuesta:**

```json
{
  "count": 10,
  "next": "http://localhost:8000/api/usuarios/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "email": "admin@ejemplo.com",
      "nombres": "Admin",
      "apellidos": "Sistema",
      "is_active": true,
      "fecha_creacion": "2023-05-20T10:30:00Z"
    },
    ...
  ]
}
```

#### Obtener Usuario

```
GET /api/usuarios/{id}/
```

**Respuesta:**

```json
{
  "id": 1,
  "email": "admin@ejemplo.com",
  "nombres": "Admin",
  "apellidos": "Sistema",
  "is_active": true,
  "fecha_creacion": "2023-05-20T10:30:00Z"
}
```

## Módulo Inventario

### Productos

#### Listar Productos

```
GET /api/inventario/productos/
```

**Parámetros de consulta:**
- `page`: Número de página
- `search`: Término de búsqueda
- `categoria`: ID de categoría
- `estado`: Estado del producto (disponible, agotado, descontinuado)
- `activo`: Estado activo (true, false)

**Respuesta:**

```json
{
  "count": 50,
  "next": "http://localhost:8000/api/inventario/productos/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "codigo": "PROD001",
      "nombre": "Producto 1",
      "descripcion": "Descripción del producto",
      "precio_compra": 10.00,
      "precio_venta": 15.00,
      "stock": 100,
      "stock_minimo": 10,
      "categoria": 1,
      "categoria_nombre": "Categoría 1",
      "imagen": "http://localhost:8000/media/productos/producto1.jpg",
      "estado": "disponible",
      "tipo": "producto",
      "iva": 12.00,
      "es_inventariable": true,
      "activo": true
    },
    ...
  ]
}
```

#### Registrar Entrada de Inventario

```
POST /api/inventario/productos/{id}/registrar_entrada/
```

**Parámetros de solicitud:**

```json
{
  "cantidad": 50,
  "origen": "compra",
  "costo_unitario": 9.50,
  "proveedor": 1,
  "documento": "FACT-001",
  "notas": "Entrada de inventario"
}
```

**Respuesta:**

```json
{
  "id": 1,
  "fecha": "2023-05-20T10:30:00Z",
  "tipo": "entrada",
  "origen": "compra",
  "producto": 1,
  "producto_nombre": "Producto 1",
  "cantidad": 50,
  "stock_anterior": 100,
  "stock_nuevo": 150,
  "costo_unitario": 9.50,
  "proveedor": 1,
  "proveedor_nombre": "Proveedor 1",
  "documento": "FACT-001",
  "notas": "Entrada de inventario"
}
```

## Módulo Ventas

### Ventas

#### Crear Venta

```
POST /api/ventas/ventas/crear_venta/
```

**Parámetros de solicitud:**

```json
{
  "cliente_id": 1,
  "tipo": "factura",
  "items": [
    {
      "producto_id": 1,
      "cantidad": 2,
      "precio_unitario": 15.00,
      "descuento": 0
    },
    {
      "producto_id": 2,
      "cantidad": 1,
      "precio_unitario": 30.00,
      "descuento": 5.00
    }
  ],
  "direccion_facturacion_id": 1,
  "direccion_envio_id": 1,
  "notas": "Venta de prueba"
}
```

**Respuesta:**

```json
{
  "id": 1,
  "numero": "F2023050001",
  "fecha": "2023-05-20T10:30:00Z",
  "cliente": 1,
  "cliente_nombre": "Cliente 1",
  "direccion_facturacion": 1,
  "direccion_envio": 1,
  "tipo": "factura",
  "estado": "borrador",
  "subtotal": 55.00,
  "iva": 6.60,
  "descuento": 5.00,
  "total": 56.60,
  "notas": "Venta de prueba",
  "detalles": [
    {
      "id": 1,
      "venta": 1,
      "producto": 1,
      "producto_nombre": "Producto 1",
      "cantidad": 2,
      "precio_unitario": 15.00,
      "descuento": 0,
      "iva": 3.60,
      "subtotal": 30.00,
      "total": 33.60
    },
    {
      "id": 2,
      "venta": 1,
      "producto": 2,
      "producto_nombre": "Producto 2",
      "cantidad": 1,
      "precio_unitario": 30.00,
      "descuento": 5.00,
      "iva": 3.00,
      "subtotal": 25.00,
      "total": 28.00
    }
  ],
  "pagos": []
}
```

## Módulo E-commerce

### Carrito

#### Obtener Carrito Actual

```
GET /api/ecommerce/carritos/actual/
```

**Respuesta:**

```json
{
  "id": 1,
  "cliente": 1,
  "sesion_id": "abc123",
  "fecha_creacion": "2023-05-20T10:30:00Z",
  "fecha_actualizacion": "2023-05-20T10:35:00Z",
  "convertido_a_pedido": false,
  "items": [
    {
      "id": 1,
      "carrito": 1,
      "producto": 1,
      "producto_nombre": "Producto 1",
      "cantidad": 2,
      "precio_unitario": 15.00,
      "impuesto_unitario": 1.80,
      "subtotal": 30.00,
      "impuestos": 3.60,
      "total": 33.60
    }
  ],
  "total_items": 2,
  "subtotal": 30.00,
  "total_impuestos": 3.60,
  "total": 33.60
}
```

#### Agregar Item al Carrito

```
POST /api/ecommerce/carritos/{id}/agregar_item/
```

**Parámetros de solicitud:**

```json
{
  "producto_id": 1,
  "cantidad": 2
}
```

**Respuesta:**

```json
{
  "id": 1,
  "carrito": 1,
  "producto": 1,
  "producto_nombre": "Producto 1",
  "cantidad": 2,
  "precio_unitario": 15.00,
  "impuesto_unitario": 1.80,
  "subtotal": 30.00,
  "impuestos": 3.60,
  "total": 33.60
}
```

## Códigos de Estado

- `200 OK`: La solicitud se ha completado correctamente
- `201 Created`: El recurso se ha creado correctamente
- `400 Bad Request`: La solicitud contiene datos inválidos
- `401 Unauthorized`: No se ha proporcionado autenticación o es inválida
- `403 Forbidden`: No se tienen permisos para acceder al recurso
- `404 Not Found`: El recurso solicitado no existe
- `500 Internal Server Error`: Error interno del servidor