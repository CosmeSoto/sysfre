from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, Count, Avg, F, ExpressionWrapper, DecimalField
from django.db.models.functions import TruncMonth, TruncDay
from django.utils import timezone
from datetime import timedelta
import csv
import xlsxwriter
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from ventas.models import Venta, DetalleVenta
from inventario.models import Producto, Movimiento
from reparaciones.models import Reparacion
from ecommerce.models import Pedido


@login_required
@permission_required('reportes.view_reporte')
def dashboard(request):
    """Vista para el dashboard de reportes."""
    # Fecha actual y hace 30 días
    hoy = timezone.now().date()
    hace_30_dias = hoy - timedelta(days=30)
    
    # Ventas de los últimos 30 días
    ventas_30_dias = Venta.objects.filter(
        fecha__date__gte=hace_30_dias,
        estado__in=['pagado', 'enviado', 'entregado']
    )
    
    # Total de ventas
    total_ventas = ventas_30_dias.aggregate(total=Sum('total'))['total'] or 0
    
    # Número de ventas
    num_ventas = ventas_30_dias.count()
    
    # Ventas por día
    ventas_por_dia = ventas_30_dias.annotate(
        dia=TruncDay('fecha')
    ).values('dia').annotate(
        total=Sum('total'),
        cantidad=Count('id')
    ).order_by('dia')
    
    # Productos más vendidos
    productos_mas_vendidos = DetalleVenta.objects.filter(
        venta__fecha__date__gte=hace_30_dias,
        venta__estado__in=['pagado', 'enviado', 'entregado']
    ).values(
        'producto__nombre'
    ).annotate(
        cantidad=Sum('cantidad'),
        total=Sum(ExpressionWrapper(
            F('precio_unitario') * F('cantidad'),
            output_field=DecimalField()
        ))
    ).order_by('-cantidad')[:10]
    
    # Reparaciones de los últimos 30 días
    reparaciones_30_dias = Reparacion.objects.filter(
        fecha_recepcion__date__gte=hace_30_dias
    )
    
    # Total de reparaciones
    total_reparaciones = reparaciones_30_dias.aggregate(total=Sum('total'))['total'] or 0
    
    # Número de reparaciones
    num_reparaciones = reparaciones_30_dias.count()
    
    # Reparaciones por estado
    reparaciones_por_estado = reparaciones_30_dias.values(
        'estado'
    ).annotate(
        cantidad=Count('id')
    ).order_by('estado')
    
    # Pedidos online de los últimos 30 días
    pedidos_30_dias = Pedido.objects.filter(
        fecha__date__gte=hace_30_dias,
        estado__in=['pagado', 'enviado', 'entregado']
    )
    
    # Total de pedidos online
    total_pedidos = pedidos_30_dias.aggregate(total=Sum('total'))['total'] or 0
    
    # Número de pedidos online
    num_pedidos = pedidos_30_dias.count()
    
    context = {
        'total_ventas': total_ventas,
        'num_ventas': num_ventas,
        'ventas_por_dia': list(ventas_por_dia),
        'productos_mas_vendidos': list(productos_mas_vendidos),
        'total_reparaciones': total_reparaciones,
        'num_reparaciones': num_reparaciones,
        'reparaciones_por_estado': list(reparaciones_por_estado),
        'total_pedidos': total_pedidos,
        'num_pedidos': num_pedidos,
    }
    
    return render(request, 'reportes/dashboard.html', context)


@login_required
@permission_required('reportes.view_reporte')
def reporte_ventas(request):
    """Vista para el reporte de ventas."""
    # Obtener parámetros
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    formato = request.GET.get('formato', 'html')
    
    # Filtrar ventas
    ventas = Venta.objects.all().order_by('-fecha')
    
    if fecha_inicio:
        ventas = ventas.filter(fecha__date__gte=fecha_inicio)
    
    if fecha_fin:
        ventas = ventas.filter(fecha__date__lte=fecha_fin)
    
    # Calcular totales
    total_ventas = ventas.aggregate(total=Sum('total'))['total'] or 0
    num_ventas = ventas.count()
    
    # Agrupar por estado
    ventas_por_estado = ventas.values('estado').annotate(
        cantidad=Count('id'),
        total=Sum('total')
    ).order_by('estado')
    
    # Exportar según formato
    if formato == 'csv':
        return exportar_ventas_csv(ventas)
    elif formato == 'excel':
        return exportar_ventas_excel(ventas)
    elif formato == 'pdf':
        return exportar_ventas_pdf(ventas)
    
    # Renderizar HTML
    context = {
        'ventas': ventas,
        'total_ventas': total_ventas,
        'num_ventas': num_ventas,
        'ventas_por_estado': ventas_por_estado,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    }
    
    return render(request, 'reportes/ventas.html', context)


@login_required
@permission_required('reportes.view_reporte')
def reporte_inventario(request):
    """Vista para el reporte de inventario."""
    # Obtener parámetros
    categoria_id = request.GET.get('categoria')
    stock_minimo = request.GET.get('stock_minimo')
    formato = request.GET.get('formato', 'html')
    
    # Filtrar productos
    productos = Producto.objects.filter(es_inventariable=True).order_by('nombre')
    
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    
    if stock_minimo == 'si':
        productos = productos.filter(stock__lte=F('stock_minimo'))
    
    # Calcular totales
    total_productos = productos.count()
    valor_inventario = productos.aggregate(
        valor=Sum(ExpressionWrapper(
            F('stock') * F('precio_compra'),
            output_field=DecimalField()
        ))
    )['valor'] or 0
    
    # Exportar según formato
    if formato == 'csv':
        return exportar_inventario_csv(productos)
    elif formato == 'excel':
        return exportar_inventario_excel(productos)
    elif formato == 'pdf':
        return exportar_inventario_pdf(productos)
    
    # Renderizar HTML
    context = {
        'productos': productos,
        'total_productos': total_productos,
        'valor_inventario': valor_inventario,
        'categoria_id': categoria_id,
        'stock_minimo': stock_minimo,
    }
    
    return render(request, 'reportes/inventario.html', context)


@login_required
@permission_required('reportes.view_reporte')
def reporte_reparaciones(request):
    """Vista para el reporte de reparaciones."""
    # Obtener parámetros
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    estado = request.GET.get('estado')
    formato = request.GET.get('formato', 'html')
    
    # Filtrar reparaciones
    reparaciones = Reparacion.objects.all().order_by('-fecha_recepcion')
    
    if fecha_inicio:
        reparaciones = reparaciones.filter(fecha_recepcion__date__gte=fecha_inicio)
    
    if fecha_fin:
        reparaciones = reparaciones.filter(fecha_recepcion__date__lte=fecha_fin)
    
    if estado:
        reparaciones = reparaciones.filter(estado=estado)
    
    # Calcular totales
    total_reparaciones = reparaciones.aggregate(total=Sum('total'))['total'] or 0
    num_reparaciones = reparaciones.count()
    
    # Agrupar por estado
    reparaciones_por_estado = reparaciones.values('estado').annotate(
        cantidad=Count('id'),
        total=Sum('total')
    ).order_by('estado')
    
    # Exportar según formato
    if formato == 'csv':
        return exportar_reparaciones_csv(reparaciones)
    elif formato == 'excel':
        return exportar_reparaciones_excel(reparaciones)
    elif formato == 'pdf':
        return exportar_reparaciones_pdf(reparaciones)
    
    # Renderizar HTML
    context = {
        'reparaciones': reparaciones,
        'total_reparaciones': total_reparaciones,
        'num_reparaciones': num_reparaciones,
        'reparaciones_por_estado': reparaciones_por_estado,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'estado': estado,
    }
    
    return render(request, 'reportes/reparaciones.html', context)


# Funciones auxiliares para exportación

def exportar_ventas_csv(ventas):
    """Exporta las ventas a CSV."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ventas.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Número', 'Fecha', 'Cliente', 'Estado', 'Subtotal', 'IVA', 'Total'])
    
    for venta in ventas:
        writer.writerow([
            venta.numero,
            venta.fecha.strftime('%d/%m/%Y %H:%M'),
            venta.cliente.nombre,
            venta.get_estado_display(),
            venta.subtotal,
            venta.iva,
            venta.total
        ])
    
    return response


def exportar_ventas_excel(ventas):
    """Exporta las ventas a Excel."""
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    
    # Formatos
    header_format = workbook.add_format({'bold': True, 'bg_color': '#4B5563', 'color': 'white'})
    date_format = workbook.add_format({'num_format': 'dd/mm/yyyy hh:mm'})
    money_format = workbook.add_format({'num_format': '$#,##0.00'})
    
    # Encabezados
    headers = ['Número', 'Fecha', 'Cliente', 'Estado', 'Subtotal', 'IVA', 'Total']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)
    
    # Datos
    for row, venta in enumerate(ventas, start=1):
        worksheet.write(row, 0, venta.numero)
        worksheet.write_datetime(row, 1, venta.fecha, date_format)
        worksheet.write(row, 2, venta.cliente.nombre)
        worksheet.write(row, 3, venta.get_estado_display())
        worksheet.write_number(row, 4, float(venta.subtotal), money_format)
        worksheet.write_number(row, 5, float(venta.iva), money_format)
        worksheet.write_number(row, 6, float(venta.total), money_format)
    
    # Ajustar anchos de columna
    for i, width in enumerate([15, 20, 30, 15, 15, 15, 15]):
        worksheet.set_column(i, i, width)
    
    workbook.close()
    output.seek(0)
    
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="ventas.xlsx"'
    
    return response


def exportar_ventas_pdf(ventas):
    """Exporta las ventas a PDF."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    
    # Título
    elements.append(Paragraph("Reporte de Ventas", title_style))
    elements.append(Paragraph(f"Fecha: {timezone.now().strftime('%d/%m/%Y')}", styles['Normal']))
    elements.append(Paragraph(" ", styles['Normal']))  # Espacio
    
    # Tabla
    data = [['Número', 'Fecha', 'Cliente', 'Estado', 'Total']]
    
    for venta in ventas:
        data.append([
            venta.numero,
            venta.fecha.strftime('%d/%m/%Y'),
            venta.cliente.nombre,
            venta.get_estado_display(),
            f"${venta.total}"
        ])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    
    # Construir PDF
    doc.build(elements)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="ventas.pdf"'
    
    return response