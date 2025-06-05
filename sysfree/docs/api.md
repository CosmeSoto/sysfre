# API Documentation

## Authentication

### Login
- **URL**: `/api/token/`
- **Method**: POST
- **Body**: `{ "email": "user@example.com", "password": "password" }`
- **Response**: `{ "access": "token", "refresh": "token" }`

### Refresh Token
- **URL**: `/api/token/refresh/`
- **Method**: POST
- **Body**: `{ "refresh": "token" }`
- **Response**: `{ "access": "token" }`

## Inventory

### List Products
- **URL**: `/api/inventario/productos/`
- **Method**: GET
- **Query Parameters**: 
  - `search`: Search term
  - `categoria`: Category ID
  - `page`: Page number
- **Response**: List of products with pagination

### Get Product
- **URL**: `/api/inventario/productos/{id}/`
- **Method**: GET
- **Response**: Product details

### Create Product
- **URL**: `/api/inventario/productos/`
- **Method**: POST
- **Body**: Product data
- **Response**: Created product

### Update Product
- **URL**: `/api/inventario/productos/{id}/`
- **Method**: PUT
- **Body**: Updated product data
- **Response**: Updated product

### Delete Product
- **URL**: `/api/inventario/productos/{id}/`
- **Method**: DELETE
- **Response**: 204 No Content

## Sales

### List Sales
- **URL**: `/api/ventas/`
- **Method**: GET
- **Query Parameters**: 
  - `search`: Search term
  - `cliente`: Customer ID
  - `fecha_inicio`: Start date
  - `fecha_fin`: End date
  - `page`: Page number
- **Response**: List of sales with pagination

### Get Sale
- **URL**: `/api/ventas/{id}/`
- **Method**: GET
- **Response**: Sale details

### Create Sale
- **URL**: `/api/ventas/`
- **Method**: POST
- **Body**: Sale data
- **Response**: Created sale

### Update Sale
- **URL**: `/api/ventas/{id}/`
- **Method**: PUT
- **Body**: Updated sale data
- **Response**: Updated sale

### Delete Sale
- **URL**: `/api/ventas/{id}/`
- **Method**: DELETE
- **Response**: 204 No Content

## Customers

### List Customers
- **URL**: `/api/clientes/`
- **Method**: GET
- **Query Parameters**: 
  - `search`: Search term
  - `page`: Page number
- **Response**: List of customers with pagination

### Get Customer
- **URL**: `/api/clientes/{id}/`
- **Method**: GET
- **Response**: Customer details

### Create Customer
- **URL**: `/api/clientes/`
- **Method**: POST
- **Body**: Customer data
- **Response**: Created customer

### Update Customer
- **URL**: `/api/clientes/{id}/`
- **Method**: PUT
- **Body**: Updated customer data
- **Response**: Updated customer

### Delete Customer
- **URL**: `/api/clientes/{id}/`
- **Method**: DELETE
- **Response**: 204 No Content

## Repairs

### List Repairs
- **URL**: `/api/reparaciones/`
- **Method**: GET
- **Query Parameters**: 
  - `search`: Search term
  - `cliente`: Customer ID
  - `estado`: Status
  - `page`: Page number
- **Response**: List of repairs with pagination

### Get Repair
- **URL**: `/api/reparaciones/{id}/`
- **Method**: GET
- **Response**: Repair details

### Create Repair
- **URL**: `/api/reparaciones/`
- **Method**: POST
- **Body**: Repair data
- **Response**: Created repair

### Update Repair
- **URL**: `/api/reparaciones/{id}/`
- **Method**: PUT
- **Body**: Updated repair data
- **Response**: Updated repair

### Delete Repair
- **URL**: `/api/reparaciones/{id}/`
- **Method**: DELETE
- **Response**: 204 No Content