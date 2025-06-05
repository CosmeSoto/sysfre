import csv
import io
import xlsxwriter
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status


def export_queryset_to_csv(queryset, fields, filename="export.csv"):
    """
    Exporta un queryset a un archivo CSV.
    
    Args:
        queryset: QuerySet a exportar
        fields: Lista de campos a incluir
        filename: Nombre del archivo
        
    Returns:
        HttpResponse con el archivo CSV
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    writer = csv.writer(response)
    
    # Escribir encabezados
    headers = [queryset.model._meta.get_field(field).verbose_name for field in fields]
    writer.writerow(headers)
    
    # Escribir datos
    for obj in queryset:
        row = []
        for field in fields:
            value = getattr(obj, field)
            if callable(value):
                value = value()
            row.append(str(value))
        writer.writerow(row)
    
    return response


def export_queryset_to_excel(queryset, fields, filename="export.xlsx"):
    """
    Exporta un queryset a un archivo Excel.
    
    Args:
        queryset: QuerySet a exportar
        fields: Lista de campos a incluir
        filename: Nombre del archivo
        
    Returns:
        HttpResponse con el archivo Excel
    """
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    
    # Formato para encabezados
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#F7F7F7',
        'border': 1
    })
    
    # Escribir encabezados
    headers = [queryset.model._meta.get_field(field).verbose_name for field in fields]
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)
    
    # Escribir datos
    for row, obj in enumerate(queryset, start=1):
        for col, field in enumerate(fields):
            value = getattr(obj, field)
            if callable(value):
                value = value()
            worksheet.write(row, col, str(value))
    
    workbook.close()
    
    # Preparar respuesta
    output.seek(0)
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


def paginate_queryset(queryset, request, view):
    """
    Pagina un queryset y devuelve la respuesta paginada.
    
    Args:
        queryset: QuerySet a paginar
        request: Request actual
        view: Vista actual
        
    Returns:
        Response con los datos paginados
    """
    page = view.paginate_queryset(queryset)
    if page is not None:
        serializer = view.get_serializer(page, many=True)
        return view.get_paginated_response(serializer.data)
    
    serializer = view.get_serializer(queryset, many=True)
    return Response(serializer.data)


def validate_request_data(serializer, data):
    """
    Valida los datos de una solicitud con un serializador.
    
    Args:
        serializer: Clase del serializador
        data: Datos a validar
        
    Returns:
        tuple: (datos_validados, respuesta_error)
    """
    serializer_instance = serializer(data=data)
    if serializer_instance.is_valid():
        return serializer_instance.validated_data, None
    
    return None, Response(
        {
            'error': True,
            'message': 'Datos inválidos',
            'details': serializer_instance.errors,
            'status_code': status.HTTP_400_BAD_REQUEST
        },
        status=status.HTTP_400_BAD_REQUEST
    )