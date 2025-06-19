from celery import shared_task
import logging
from django.core.mail import EmailMessage
from ventas.models import Venta
from fiscal.services.comprobante_service import ComprobanteService
from reportes.services.ride_generator_service import RIDEGeneratorService
from core.models import Empresa

logger = logging.getLogger('sysfree')

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def procesar_facturacion_electronica_task(self, venta_id):
    """
    Tarea asíncrona para procesar una factura electrónica completa.
    Genera XML, firma, envía, autoriza, genera RIDE y notifica al cliente.
    """
    try:
        venta = Venta.objects.get(pk=venta_id)
        empresa = Empresa.objects.first()

        if not empresa or not empresa.ruta_certificado or not empresa.clave_certificado:
            logger.error(f"Facturación electrónica no configurada para la empresa. Venta ID: {venta_id}")
            return

        # 1. Generar XML
        logger.info(f"Generando XML para venta {venta.numero}...")
        xml_string = ComprobanteService.generar_xml_factura(venta)

        # 2. Firmar XML
        logger.info(f"Firmando XML para venta {venta.numero}...")
        xml_firmado = ComprobanteService.firmar_comprobante(
            xml_string,
            empresa.ruta_certificado,
            empresa.clave_certificado
        )

        # 3. Enviar al SRI
        logger.info(f"Enviando al SRI la venta {venta.numero}...")
        respuesta_recepcion = ComprobanteService.enviar_comprobante(xml_firmado)

        if respuesta_recepcion.get('estado') != 'RECIBIDA':
            mensaje_error = f"Error en la recepción del SRI para la venta {venta.numero}: {respuesta_recepcion.get('mensajes')}"
            logger.error(mensaje_error)
            raise Exception(mensaje_error)

        # 4. Autorizar comprobante
        logger.info(f"Autorizando en el SRI la venta {venta.numero}...")
        respuesta_autorizacion = ComprobanteService.autorizar_comprobante(venta.clave_acceso)
        
        autorizacion = respuesta_autorizacion.get('autorizaciones', {}).get('autorizacion', [{}])[0]
        estado_autorizacion = autorizacion.get('estado')

        if estado_autorizacion != 'AUTORIZADO':
            mensaje_error = f"Comprobante no autorizado para la venta {venta.numero}: {autorizacion.get('mensajes')}"
            logger.error(mensaje_error)
            raise Exception(mensaje_error)
            
        # 5. Actualizar Venta y Generar RIDE
        logger.info(f"Venta {venta.numero} autorizada. Generando RIDE...")
        venta.numero_autorizacion = autorizacion.get('numeroAutorizacion')
        venta.fecha_autorizacion = autorizacion.get('fechaAutorizacion')
        venta.estado = 'emitida' # O el estado que corresponda
        venta.save()

        pdf_ride = RIDEGeneratorService.generar_ride_factura(venta)

        # 6. Notificar al cliente
        logger.info(f"Enviando notificación al cliente para la venta {venta.numero}...")
        email = EmailMessage(
            subject=f"Factura Electrónica {venta.numero}",
            body=f"Estimado/a {venta.cliente.nombre_completo},\n\nAdjuntamos su factura electrónica.\n\nGracias por su compra.",
            from_email=empresa.email,
            to=[venta.cliente.email],
        )
        email.attach(f'factura-{venta.numero}.xml', xml_firmado, 'application/xml')
        email.attach(f'factura-{venta.numero}.pdf', pdf_ride, 'application/pdf')
        email.send()

        logger.info(f"Proceso de facturación electrónica completado para la venta {venta.numero}.")

    except Exception as e:
        logger.error(f"Error en el procesamiento de la facturación electrónica para la venta {venta_id}: {e}")
        self.retry(exc=e)