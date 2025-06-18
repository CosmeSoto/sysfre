from rest_framework import views, permissions, status
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from ventas.models import Venta, DetalleVenta
from clientes.models import Cliente
from inventario.models import Producto, MovimientoInventario


class ReporteVentasView(views.APIView):
    """Vista para el reporte de ventas."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Obtener ventas del último año
        fecha_inicio = timezone.now() - timedelta(days=365)
        ventas = Venta.objects.filter(fecha__gte=fecha_inicio)
        
        # Calcular total de ventas
        total_ventas = sum(venta.total for venta in ventas)
        
        # Calcular ventas por mes
        ventas_por_mes = {}
        for venta in ventas:
            mes = venta.fecha.strftime('%Y-%m')
            if mes not in ventas_por_mes:
                ventas_por_mes[mes] = 0
            ventas_por_mes[mes] += venta.total
        
        return Response({
            'total_ventas': total_ventas,
            'ventas_por_mes': ventas_por_mes
        })


class ReporteVentasPorPeriodoView(views.APIView):
    """Vista para el reporte de ventas por periodo."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        
        if not fecha_inicio or not fecha_fin:
            return Response(
                {'error': 'Se requieren los parámetros fecha_inicio y fecha_fin'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ventas = Venta.objects.filter(fecha__range=[fecha_inicio, fecha_fin])
        
        # Calcular total de ventas
        total_ventas = sum(venta.total for venta in ventas)
        
        return Response({
            'total_ventas': total_ventas,
            'ventas': [
                {
                    'id': venta.id,
                    'numero': venta.numero,
                    'cliente': venta.cliente.nombre_completo if venta.cliente else 'Consumidor Final',
                    'fecha': venta.fecha,
                    'total': venta.total
                }
                for venta in ventas
            ]
        })


class ReporteProductosMasVendidosView(views.APIView):
    """Vista para el reporte de productos más vendidos."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Obtener detalles de ventas
        detalles = DetalleVenta.objects.all()
        
        # Calcular cantidad vendida por producto
        productos_vendidos = {}
        for detalle in detalles:
            if detalle.producto_id not in productos_vendidos:
                productos_vendidos[detalle.producto_id] = {
                    'producto': detalle.producto,
                    'cantidad': 0,
                    'total': 0
                }
            productos_vendidos[detalle.producto_id]['cantidad'] += detalle.cantidad
            productos_vendidos[detalle.producto_id]['total'] += detalle.total
        
        # Ordenar por cantidad vendida
        productos = sorted(
            productos_vendidos.values(),
            key=lambda x: x['cantidad'],
            reverse=True
        )
        
        return Response({
            'productos': [
                {
                    'id': p['producto'].id,
                    'codigo': p['producto'].codigo,
                    'nombre': p['producto'].nombre,
                    'cantidad_vendida': p['cantidad'],
                    'total_vendido': p['total']
                }
                for p in productos[:10]  # Top 10
            ]
        })


class ReporteClientesFrecuentesView(views.APIView):
    """Vista para el reporte de clientes frecuentes."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Obtener ventas
        ventas = Venta.objects.all()
        
        # Calcular compras por cliente
        clientes_compras = {}
        for venta in ventas:
            if not venta.cliente_id:
                continue
                
            if venta.cliente_id not in clientes_compras:
                clientes_compras[venta.cliente_id] = {
                    'cliente': venta.cliente,
                    'compras': 0,
                    'total': 0
                }
            clientes_compras[venta.cliente_id]['compras'] += 1
            clientes_compras[venta.cliente_id]['total'] += venta.total
        
        # Ordenar por número de compras
        clientes = sorted(
            clientes_compras.values(),
            key=lambda x: x['compras'],
            reverse=True
        )
        
        return Response({
            'clientes': [
                {
                    'id': c['cliente'].id,
                    'nombre': c['cliente'].nombre_completo,
                    'compras': c['compras'],
                    'total_comprado': c['total']
                }
                for c in clientes[:10]  # Top 10
            ]
        })


class ReporteInventarioView(views.APIView):
    """Vista para el reporte de inventario."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Obtener productos inventariables
        productos = Producto.objects.filter(es_inventariable=True)
        
        return Response({
            'productos': [
                {
                    'id': p.id,
                    'codigo': p.codigo,
                    'nombre': p.nombre,
                    'stock': p.stock,
                    'precio_compra': p.precio_compra,
                    'precio_venta': p.precio_venta,
                    'valor_inventario': p.stock * p.precio_compra
                }
                for p in productos
            ]
        })


class ReporteMovimientosInventarioView(views.APIView):
    """Vista para el reporte de movimientos de inventario."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        producto_id = request.query_params.get('producto_id')
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        
        # Filtrar movimientos
        movimientos = MovimientoInventario.objects.all()
        
        if producto_id:
            movimientos = movimientos.filter(producto_id=producto_id)
            
        if fecha_inicio and fecha_fin:
            movimientos = movimientos.filter(fecha__range=[fecha_inicio, fecha_fin])
        
        return Response({
            'movimientos': [
                {
                    'id': m.id,
                    'tipo': m.tipo,
                    'origen': m.origen,
                    'producto': m.producto.nombre,
                    'cantidad': m.cantidad,
                    'stock_anterior': m.stock_anterior,
                    'stock_nuevo': m.stock_nuevo,
                    'fecha': m.fecha
                }
                for m in movimientos
            ]
        })


class ReporteProductosBajoStockView(views.APIView):
    """Vista para el reporte de productos con bajo stock."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        from reportes.services.stock_bajo_report_service import StockBajoReportService
        
        # Obtener umbral personalizado si se proporciona
        umbral = request.query_params.get('umbral')
        if umbral:
            try:
                umbral = int(umbral)
            except ValueError:
                umbral = None
        else:
            umbral = None
        
        # Generar reporte
        reporte = StockBajoReportService.generar_reporte(umbral_personalizado=umbral)
        
        return Response(reporte)