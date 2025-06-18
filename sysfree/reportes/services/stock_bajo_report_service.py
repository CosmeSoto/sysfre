"""
Servicio para generar reportes de productos con stock bajo.
"""
from django.db.models import F, ExpressionWrapper, BooleanField
from inventario.models import Producto

class StockBajoReportService:
    """Servicio para generar reportes de productos con stock bajo."""
    
    @staticmethod
    def generar_reporte(umbral_personalizado=None):
        """
        Genera un reporte de productos con stock bajo.
        
        Args:
            umbral_personalizado (int, optional): Umbral personalizado para considerar stock bajo.
                                                Si es None, se usa el stock_minimo de cada producto.
        
        Returns:
            dict: Reporte de productos con stock bajo
        """
        # Obtener productos inventariables y activos
        productos = Producto.objects.filter(es_inventariable=True, activo=True)
        
        if umbral_personalizado is not None:
            # Usar umbral personalizado
            productos_stock_bajo = productos.filter(stock__lte=umbral_personalizado)
        else:
            # Usar stock_minimo de cada producto
            productos_stock_bajo = productos.filter(stock__lte=F('stock_minimo'))
        
        # Calcular porcentaje de stock respecto al mínimo
        productos_stock_bajo = productos_stock_bajo.annotate(
            porcentaje_stock=ExpressionWrapper(
                100 * F('stock') / F('stock_minimo'),
                output_field=models.FloatField()
            )
        )
        
        # Ordenar por porcentaje de stock (ascendente)
        productos_stock_bajo = productos_stock_bajo.order_by('porcentaje_stock')
        
        # Preparar datos para el reporte
        datos_reporte = {
            'productos': [
                {
                    'id': p.id,
                    'codigo': p.codigo,
                    'nombre': p.nombre,
                    'stock_actual': p.stock,
                    'stock_minimo': p.stock_minimo,
                    'porcentaje_stock': round(p.porcentaje_stock, 2) if p.stock_minimo > 0 else 0,
                    'precio_compra': p.precio_compra,
                    'precio_venta': p.precio_venta,
                    'categoria': p.categoria.nombre if p.categoria else 'Sin categoría',
                    'proveedor': p.proveedor.nombre if hasattr(p, 'proveedor') and p.proveedor else 'Sin proveedor'
                }
                for p in productos_stock_bajo
            ],
            'total_productos': productos_stock_bajo.count(),
            'umbral_usado': umbral_personalizado if umbral_personalizado is not None else 'Stock mínimo de cada producto'
        }
        
        return datos_reporte