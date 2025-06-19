"""
Servicio para gestionar comprobantes fiscales.
"""
from django.db import transaction
from django.utils import timezone
import xml.etree.ElementTree as ET
from xml.dom import minidom
from core.services import IVAService
from ..models import Comprobante
from ventas.models import Venta
from ..utils.sri_utils import generar_clave_acceso
from core.models import Empresa
import base64
import hashlib
import xml.etree.ElementTree as ET
from xml.dom import minidom
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import requests


class ComprobanteService:
    """Servicio para gestionar comprobantes fiscales."""
    
    @classmethod
    @transaction.atomic
    def crear_comprobante(cls, numero, tipo, fecha_emision, proveedor, subtotal, 
                         items_iva=None, usuario=None):
        """
        Crea un comprobante fiscal.
        
        Args:
            numero: Número del comprobante
            tipo: Tipo de comprobante
            fecha_emision: Fecha de emisión
            proveedor: Proveedor
            subtotal: Subtotal
            items_iva: Lista de diccionarios con base_imponible y tipo_iva_id
            usuario: Usuario que crea el comprobante
            
        Returns:
            Comprobante: Comprobante creado
        """
        # Calcular impuestos usando el servicio IVA
        impuestos = 0
        if items_iva:
            for item in items_iva:
                base_imponible = item.get('base_imponible', 0)
                tipo_iva = None
                
                if 'tipo_iva_id' in item:
                    tipo_iva = IVAService.get_by_id(item['tipo_iva_id'])
                
                monto_iva, _ = IVAService.calcular_iva(base_imponible, tipo_iva)
                impuestos += monto_iva
        
        # Crear el comprobante
        comprobante = Comprobante(
            numero=numero,
            tipo=tipo,
            fecha_emision=fecha_emision,
            proveedor=proveedor,
            subtotal=subtotal,
            impuestos=impuestos,
            total=subtotal + impuestos,
            estado='borrador'
        )
        
        if usuario:
            comprobante.creado_por = usuario
            comprobante.modificado_por = usuario
        
        comprobante.save()
        return comprobante
    
    @classmethod
    def emitir_comprobante(cls, comprobante, usuario=None):
        """
        Emite un comprobante fiscal.
        
        Args:
            comprobante: Comprobante a emitir
            usuario: Usuario que emite el comprobante
            
        Returns:
            Comprobante: Comprobante emitido
        """
        if comprobante.estado != 'borrador':
            return comprobante
        
        comprobante.estado = 'emitido'
        
        if usuario:
            comprobante.modificado_por = usuario
        
        comprobante.save(update_fields=['estado', 'modificado_por'])
        return comprobante

    @classmethod
    def generar_xml_factura(cls, venta: Venta):
        """
        Genera el archivo XML para una factura según la especificación del SRI.
        """
        empresa = Empresa.objects.first() # Asumimos una sola empresa
        if not empresa:
            raise ValueError("No se ha configurado una empresa en el sistema.")

        # 1. Generar Clave de Acceso
        serie_parts = venta.numero.split('-')
        if len(serie_parts) != 3:
            raise ValueError("El número de factura no tiene el formato correcto (ej. 001-001-000000123)")
        
        serie = f"{serie_parts[0]}{serie_parts[1]}"
        secuencial = serie_parts[2]

        clave_acceso = generar_clave_acceso(
            fecha_emision=venta.fecha,
            tipo_comprobante='01', # 01 = Factura
            ruc=empresa.ruc,
            ambiente=empresa.ambiente_facturacion,
            serie=serie,
            numero_comprobante=secuencial,
            tipo_emision='1' # 1 = Emisión Normal
        )
        venta.clave_acceso = clave_acceso
        venta.save(update_fields=['clave_acceso'])

        # 2. Construir el XML
        xml_factura = ET.Element('factura', id='comprobante', version='1.1.0')
        
        # Info Tributaria
        info_tributaria = ET.SubElement(xml_factura, 'infoTributaria')
        ET.SubElement(info_tributaria, 'ambiente').text = empresa.ambiente_facturacion
        ET.SubElement(info_tributaria, 'tipoEmision').text = '1'
        ET.SubElement(info_tributaria, 'razonSocial').text = empresa.nombre
        ET.SubElement(info_tributaria, 'nombreComercial').text = empresa.nombre_comercial or empresa.nombre
        ET.SubElement(info_tributaria, 'ruc').text = empresa.ruc
        ET.SubElement(info_tributaria, 'claveAcceso').text = clave_acceso
        ET.SubElement(info_tributaria, 'codDoc').text = '01'
        ET.SubElement(info_tributaria, 'estab').text = serie_parts[0]
        ET.SubElement(info_tributaria, 'ptoEmi').text = serie_parts[1]
        ET.SubElement(info_tributaria, 'secuencial').text = secuencial
        ET.SubElement(info_tributaria, 'dirMatriz').text = empresa.direccion

        # Info Factura
        info_factura = ET.SubElement(xml_factura, 'infoFactura')
        ET.SubElement(info_factura, 'fechaEmision').text = venta.fecha.strftime('%d/%m/%Y')
        ET.SubElement(info_factura, 'dirEstablecimiento').text = empresa.direccion # Asumir misma dirección
        # ET.SubElement(info_factura, 'contribuyenteEspecial').text = '12345' # Si aplica
        ET.SubElement(info_factura, 'obligadoContabilidad').text = 'SI' # O 'NO'
        
        tipo_identificacion_comprador = venta.cliente.get_tipo_identificacion_sri()
        ET.SubElement(info_factura, 'tipoIdentificacionComprador').text = tipo_identificacion_comprador
        ET.SubElement(info_factura, 'razonSocialComprador').text = venta.cliente.nombre_completo
        ET.SubElement(info_factura, 'identificacionComprador').text = venta.cliente.identificacion
        ET.SubElement(info_factura, 'totalSinImpuestos').text = f"{venta.subtotal:.2f}"
        ET.SubElement(info_factura, 'totalDescuento').text = f"{venta.descuento:.2f}"

        # totalConImpuestos
        total_con_impuestos = ET.SubElement(info_factura, 'totalConImpuestos')
        
        # Agrupar detalles por tipo de IVA
        detalles_por_iva = {}
        for detalle in venta.detalles.all():
            if detalle.tipo_iva.codigo not in detalles_por_iva:
                detalles_por_iva[detalle.tipo_iva.codigo] = {
                    'baseImponible': 0,
                    'valor': 0,
                    'tarifa': detalle.tipo_iva.porcentaje
                }
            detalles_por_iva[detalle.tipo_iva.codigo]['baseImponible'] += detalle.subtotal
            detalles_por_iva[detalle.tipo_iva.codigo]['valor'] += detalle.iva

        for codigo_iva, valores in detalles_por_iva.items():
            total_impuesto = ET.SubElement(total_con_impuestos, 'totalImpuesto')
            ET.SubElement(total_impuesto, 'codigo').text = '2' # 2 = IVA
            ET.SubElement(total_impuesto, 'codigoPorcentaje').text = codigo_iva
            ET.SubElement(total_impuesto, 'baseImponible').text = f"{valores['baseImponible']:.2f}"
            ET.SubElement(total_impuesto, 'valor').text = f"{valores['valor']:.2f}"

        ET.SubElement(info_factura, 'propina').text = '0.00'
        ET.SubElement(info_factura, 'importeTotal').text = f"{venta.total:.2f}"
        ET.SubElement(info_factura, 'moneda').text = 'DOLAR'

        # Detalles
        detalles = ET.SubElement(xml_factura, 'detalles')
        for detalle in venta.detalles.all():
            detalle_xml = ET.SubElement(detalles, 'detalle')
            ET.SubElement(detalle_xml, 'codigoPrincipal').text = detalle.producto.codigo
            ET.SubElement(detalle_xml, 'descripcion').text = detalle.producto.nombre
            ET.SubElement(detalle_xml, 'cantidad').text = f"{detalle.cantidad:.2f}"
            ET.SubElement(detalle_xml, 'precioUnitario').text = f"{detalle.precio_unitario:.2f}"
            ET.SubElement(detalle_xml, 'descuento').text = f"{detalle.descuento:.2f}"
            ET.SubElement(detalle_xml, 'precioTotalSinImpuesto').text = f"{detalle.subtotal:.2f}"
            
            impuestos_detalle = ET.SubElement(detalle_xml, 'impuestos')
            impuesto = ET.SubElement(impuestos_detalle, 'impuesto')
            ET.SubElement(impuesto, 'codigo').text = '2' # 2 = IVA
            ET.SubElement(impuesto, 'codigoPorcentaje').text = detalle.tipo_iva.codigo
            ET.SubElement(impuesto, 'tarifa').text = f"{detalle.tipo_iva.porcentaje:.2f}"
            ET.SubElement(impuesto, 'baseImponible').text = f"{detalle.subtotal:.2f}"
            ET.SubElement(impuesto, 'valor').text = f"{detalle.iva:.2f}"

        # Info Adicional
        info_adicional = ET.SubElement(xml_factura, 'infoAdicional')
        campo_adicional_email = ET.SubElement(info_adicional, 'campoAdicional', nombre='Email')
        campo_adicional_email.text = venta.cliente.email

        # 3. Formatear y devolver el XML
        xml_str = ET.tostring(xml_factura, encoding='utf-8')
        dom = minidom.parseString(xml_str)
        return dom.toprettyxml(indent="  ", encoding='utf-8').decode('utf-8')

    @classmethod
    def firmar_comprobante(cls, xml_string, certificado_path, clave_certificado):
        """
        Firma un comprobante XML con el certificado digital (implementación manual).
        """
        if not certificado_path or not clave_certificado:
            raise ValueError("La ruta del certificado y la clave no pueden estar vacías.")

        try:
            with open(certificado_path, "rb") as f:
                p12_data = f.read()
        except FileNotFoundError:
            raise ValueError(f"No se encontró el archivo del certificado en: {certificado_path}")

        private_key, certificate, _ = pkcs12.load_key_and_certificates(
            p12_data,
            clave_certificado.encode()
        )

        # Parsear el XML
        root = ET.fromstring(xml_string.encode('utf-8'))

        # Crear la estructura de la firma
        signature = ET.Element("Signature", {"xmlns": "http://www.w3.org/2000/09/xmldsig#"})
        signed_info = ET.SubElement(signature, "SignedInfo")
        
        # Canonicalization Method
        c14n = ET.SubElement(signed_info, "CanonicalizationMethod", Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315")

        # Signature Method
        sig_method = ET.SubElement(signed_info, "SignatureMethod", Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1")

        # Reference
        reference = ET.SubElement(signed_info, "Reference", URI="#comprobante")
        transforms = ET.SubElement(reference, "Transforms")
        ET.SubElement(transforms, "Transform", Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature")
        
        digest_method = ET.SubElement(reference, "DigestMethod", Algorithm="http://www.w3.org/2000/09/xmldsig#sha1")
        
        # Calcular el DigestValue
        # Nota: La canonalización para el digest es un proceso complejo.
        # Esta es una aproximación. Para producción se requiere una librería que lo haga exacto.
        c14n_comprobante = ET.tostring(root, method='xml', encoding='utf-8')
        digest_value = base64.b64encode(hashlib.sha1(c14n_comprobante).digest()).decode()
        ET.SubElement(reference, "DigestValue").text = digest_value

        # Calcular el SignatureValue
        # La canonalización de SignedInfo también es crítica.
        c14n_signed_info = ET.tostring(signed_info, method='xml', encoding='utf-8')
        signature_hash = private_key.sign(
            c14n_signed_info,
            padding.PKCS1v15(),
            hashes.SHA1()
        )
        signature_value = base64.b64encode(signature_hash).decode()
        
        ET.SubElement(signature, "SignatureValue").text = signature_value

        # KeyInfo
        key_info = ET.SubElement(signature, "KeyInfo")
        x509_data = ET.SubElement(key_info, "X509Data")
        x509_certificate = ET.SubElement(x509_data, "X509Certificate")
        x509_certificate.text = base64.b64encode(certificate.public_bytes(encoding=hashes.Encoding.DER)).decode()

        root.append(signature)
        
        xml_str = ET.tostring(root, encoding='utf-8')
        dom = minidom.parseString(xml_str)
        return dom.toprettyxml(indent="  ", encoding='utf-8').decode('utf-8')

    @classmethod
    def enviar_comprobante(cls, xml_firmado_str):
        """
        Envía un comprobante firmado al web service de recepción del SRI.
        """
        empresa = Empresa.objects.first()
        if not empresa:
            raise ValueError("No se ha configurado una empresa en el sistema.")

        if empresa.ambiente_facturacion == '1': # Pruebas
            url = empresa.url_recepcion_pruebas
        else: # Producción
            url = empresa.url_recepcion_produccion
            
        headers = {'Content-Type': 'application/soap+xml;charset=UTF-8'}
        
        # El XML debe estar en base64 dentro del sobre SOAP
        xml_base64 = base64.b64encode(xml_firmado_str.encode('utf-8')).decode('utf-8')
        
        soap_body = f"""
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ec="http://ec.gob.sri.ws.recepcion">
           <soapenv:Header/>
           <soapenv:Body>
              <ec:validarComprobante>
                 <xml>{xml_base64}</xml>
              </ec:validarComprobante>
           </soapenv:Body>
        </soapenv:Envelope>
        """
        
        try:
            response = requests.post(url, data=soap_body.encode('utf-8'), headers=headers, timeout=10)
            response.raise_for_status()
            return cls._parse_respuesta_sri(response.text)
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error de conexión con el SRI: {e}")

    @classmethod
    def autorizar_comprobante(cls, clave_acceso):
        """
        Consulta el web service de autorización del SRI para un comprobante.
        """
        empresa = Empresa.objects.first()
        if not empresa:
            raise ValueError("No se ha configurado una empresa en el sistema.")

        if empresa.ambiente_facturacion == '1': # Pruebas
            url = empresa.url_autorizacion_pruebas
        else: # Producción
            url = empresa.url_autorizacion_produccion

        headers = {'Content-Type': 'application/soap+xml;charset=UTF-8'}
        
        soap_body = f"""
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ec="http://ec.gob.sri.ws.autorizacion">
           <soapenv:Header/>
           <soapenv:Body>
              <ec:autorizacionComprobante>
                 <claveAccesoComprobante>{clave_acceso}</claveAccesoComprobante>
              </ec:autorizacionComprobante>
           </soapenv:Body>
        </soapenv:Envelope>
        """
        
        try:
            response = requests.post(url, data=soap_body.encode('utf-8'), headers=headers, timeout=10)
            response.raise_for_status()
            return cls._parse_respuesta_sri(response.text)
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error de conexión con el SRI: {e}")

    @staticmethod
    def _parse_respuesta_sri(response_text):
        """
        Parsea la respuesta XML del SRI para extraer información relevante.
        """
        try:
            root = ET.fromstring(response_text)
            # Namespace-aware find
            ns = {
                'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
                'ns2': 'http://ec.gob.sri.ws.recepcion', # O autorizacion
            }
            body = root.find('soap:Body', ns)
            
            # Extraer estado y mensajes
            estado = body.find('.//estado').text
            mensajes = []
            for msg in body.findall('.//mensaje'):
                mensajes.append({
                    'identificador': msg.find('identificador').text,
                    'mensaje': msg.find('mensaje').text,
                    'tipo': msg.find('tipo').text,
                    'informacionAdicional': msg.find('informacionAdicional').text if msg.find('informacionAdicional') is not None else ''
                })
            
            return {'estado': estado, 'mensajes': mensajes}
        except Exception as e:
            return {'estado': 'ERROR_PARSE', 'mensajes': [{'mensaje': str(e)}]}
    
    @classmethod
    def anular_comprobante(cls, comprobante, usuario=None):
        """
        Anula un comprobante fiscal.
        
        Args:
            comprobante: Comprobante a anular
            usuario: Usuario que anula el comprobante
            
        Returns:
            Comprobante: Comprobante anulado
        """
        if comprobante.estado == 'anulado':
            return comprobante
        
        comprobante.estado = 'anulado'
        
        if usuario:
            comprobante.modificado_por = usuario
        
        comprobante.save(update_fields=['estado', 'modificado_por'])
        return comprobante