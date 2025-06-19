import random
from datetime import datetime

def _calcular_digito_verificador(clave):
    """
    Calcula el dígito verificador usando el algoritmo Módulo 11.
    """
    factores = [7, 6, 5, 4, 3, 2]
    suma = 0
    for i, digito in enumerate(reversed(clave)):
        suma += int(digito) * factores[i % 6]
    
    resultado = 11 - (suma % 11)
    if resultado == 11:
        return 0
    if resultado == 10:
        return 1
    return resultado

def generar_clave_acceso(fecha_emision, tipo_comprobante, ruc, ambiente, serie, numero_comprobante, tipo_emision='1'):
    """
    Genera la clave de acceso de 49 dígitos para un comprobante electrónico del SRI.

    Args:
        fecha_emision (date): Fecha de emisión del comprobante.
        tipo_comprobante (str): Código del tipo de comprobante (ej. '01' para factura).
        ruc (str): RUC del emisor (13 dígitos).
        ambiente (str): Código del ambiente ('1' para pruebas, '2' para producción).
        serie (str): Serie del comprobante (ej. '001001').
        numero_comprobante (str): Número secuencial del comprobante (9 dígitos).
        tipo_emision (str): Tipo de emisión ('1' para normal).

    Returns:
        str: La clave de acceso de 49 dígitos.
    """
    if not isinstance(fecha_emision, datetime):
        raise TypeError("fecha_emision debe ser un objeto datetime.date")
    if not ruc or len(ruc) != 13:
        raise ValueError("El RUC debe tener 13 dígitos.")
    if len(serie) != 6:
        raise ValueError("La serie debe tener 6 dígitos (ej. '001001').")
    if len(numero_comprobante) != 9:
        raise ValueError("El número de comprobante debe tener 9 dígitos.")

    fecha_str = fecha_emision.strftime('%d%m%Y')
    
    # El código numérico es un secuencial de 8 dígitos. Usaremos una parte aleatoria
    # para asegurar unicidad, aunque en un sistema real podría venir de una secuencia.
    codigo_numerico = str(random.randint(10000000, 99999999))

    clave_sin_dv = (
        f"{fecha_str}"
        f"{tipo_comprobante}"
        f"{ruc}"
        f"{ambiente}"
        f"{serie}"
        f"{numero_comprobante}"
        f"{codigo_numerico}"
        f"{tipo_emision}"
    )

    if len(clave_sin_dv) != 48:
        raise ValueError(f"La clave sin dígito verificador debe tener 48 dígitos, pero tiene {len(clave_sin_dv)}.")

    digito_verificador = _calcular_digito_verificador(clave_sin_dv)
    
    clave_acceso = f"{clave_sin_dv}{digito_verificador}"
    
    return clave_acceso