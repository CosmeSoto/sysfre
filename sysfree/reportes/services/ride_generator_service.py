import base64
from io import BytesIO
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
from weasyprint import FontConfiguration
import qrcode

class RIDEGeneratorService:
    """
    Servicio para generar la representación impresa (RIDE) de comprobantes electrónicos.
    """

    @staticmethod
    def _generar_qr_code(clave_acceso):
        """Genera un código QR para la clave de acceso y lo devuelve como una imagen base64."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(clave_acceso)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"

    @classmethod
    def generar_ride_factura(cls, venta):
        """
        Genera el RIDE para una factura de venta.

        Args:
            venta (Venta): La instancia de la venta autorizada.

        Returns:
            bytes: El contenido del PDF generado.
        """
        if not venta.clave_acceso or not venta.fecha_autorizacion:
            raise ValueError("La venta no parece estar autorizada por el SRI.")

        qr_code_img = cls._generar_qr_code(venta.clave_acceso)

        context = {
            'venta': venta,
            'empresa': venta.cliente.empresa, # Asumiendo que el cliente tiene una empresa asociada
            'detalles': venta.detalles.all(),
            'qr_code': qr_code_img,
        }
        
        html_string = render_to_string('reportes/factura_ride.html', context)
        
        font_config = FontConfiguration()
        html = HTML(string=html_string)
        
        pdf_bytes = html.write_pdf(font_config=font_config)
        
        return pdf_bytes