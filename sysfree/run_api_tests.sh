#!/bin/bash

# Script para ejecutar todos los tests de API

echo "Ejecutando tests de API..."
echo "=========================="

# Cambiar al directorio del proyecto
cd /home/djcos/Descargas/freecom/sysfree

# Ejecutar tests de API
echo "Ejecutando tests de API Core..."
python manage.py test api.tests.test_api_core

echo "Ejecutando tests de API Clientes..."
python manage.py test clientes.tests.test_api

echo "Ejecutando tests de API Inventario..."
python manage.py test inventario.tests.test_api

echo "Ejecutando tests de API Ventas..."
python manage.py test ventas.tests.test_api

echo "Ejecutando tests de API Ecommerce..."
python manage.py test ecommerce.tests.test_api

echo "Ejecutando tests de API Reparaciones..."
python manage.py test reparaciones.tests.test_api

echo "Ejecutando tests de API Fiscal..."
python manage.py test fiscal.tests.test_api

echo "Ejecutando tests de API Reportes..."
python manage.py test reportes.tests.test_api

echo "=========================="
echo "Tests de API completados."