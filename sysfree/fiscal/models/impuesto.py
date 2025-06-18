"""
Este archivo es un proxy para utilizar el modelo TipoIVA del módulo core.
En lugar de crear un nuevo modelo Impuesto, utilizamos el modelo TipoIVA existente.
"""
from core.models.tipo_iva import TipoIVA

# Alias para usar TipoIVA como Impuesto
Impuesto = TipoIVA