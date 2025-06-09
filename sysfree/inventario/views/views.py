from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from inventario.models import Categoria, Producto, Proveedor, MovimientoInventario
from inventario.forms import CategoriaForm, ProductoForm, ProveedorForm, MovimientoEntradaForm, MovimientoSalidaForm
from inventario.services.inventario_service import InventarioService


@login_required
def producto_list(request):
    """Vista para listar productos."""
    search_query = request.GET.get('search', '')
    categoria_id = request.GET.get('categoria', '')
    estado = request.GET.get('estado', '')
    
    productos = Producto.objects.filter(activo=True)
    
    # Aplicar filtros
    if search_query:
        productos = productos.filter(
            Q(nombre__icontains=search_query) | 
            Q(codigo__icontains=search_query) |
            Q(descripcion__icontains=search_query)
        )
    
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    
    if estado:
        productos = productos.filter(estado=estado)
    
    # Ordenar
    productos = productos.order_by('nombre')
    
    # Paginación
    paginator = Paginator(productos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Obtener categorías para el filtro
    categorias = Categoria.objects.filter(activo=True)
    
    context = {
        'page_obj': page_obj,
        'categorias': categorias,
        'search_query': search_query,
        'categoria_id': categoria_id,
        'estado': estado,
    }
    
    return render(request, 'inventario/producto_list.html', context)


@login_required
def producto_detail(request, pk):
    """Vista para ver detalles de un producto."""
    producto = get_object_or_404(Producto, pk=pk)
    movimientos = MovimientoInventario.objects.filter(producto=producto).order_by('-fecha')[:10]
    
    context = {
        'producto': producto,
        'movimientos': movimientos,
    }
    
    return render(request, 'inventario/producto_detail.html', context)


@login_required
def producto_create(request):
    """Vista para crear un producto."""
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save(commit=False)
            producto.creado_por = request.user
            producto.modificado_por = request.user
            producto.save()
            messages.success(request, 'Producto creado correctamente.')
            return redirect('inventario:producto_detail', pk=producto.pk)
    else:
        form = ProductoForm()
    
    context = {
        'form': form,
        'title': 'Crear Producto',
    }
    
    return render(request, 'inventario/producto_form.html', context)


@login_required
def producto_update(request, pk):
    """Vista para actualizar un producto."""
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            producto = form.save(commit=False)
            producto.modificado_por = request.user
            producto.save()
            messages.success(request, 'Producto actualizado correctamente.')
            return redirect('inventario:producto_detail', pk=producto.pk)
    else:
        form = ProductoForm(instance=producto)
    
    context = {
        'form': form,
        'producto': producto,
        'title': 'Editar Producto',
    }
    
    return render(request, 'inventario/producto_form.html', context)


@login_required
def producto_delete(request, pk):
    """Vista para eliminar un producto."""
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        producto.activo = False
        producto.modificado_por = request.user
        producto.save()
        messages.success(request, 'Producto eliminado correctamente.')
        return redirect('inventario:producto_list')
    
    context = {
        'producto': producto,
    }
    
    return render(request, 'inventario/producto_confirm_delete.html', context)


@login_required
def entrada_inventario(request, pk):
    """Vista para registrar una entrada de inventario."""
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        form = MovimientoEntradaForm(request.POST)
        if form.is_valid():
            try:
                movimiento = InventarioService.registrar_entrada(
                    producto=producto,
                    cantidad=form.cleaned_data['cantidad'],
                    origen=form.cleaned_data['origen'],
                    costo_unitario=form.cleaned_data['costo_unitario'],
                    proveedor=form.cleaned_data['proveedor'],
                    documento=form.cleaned_data['documento'],
                    notas=form.cleaned_data['notas'],
                    usuario=request.user
                )
                messages.success(request, 'Entrada de inventario registrada correctamente.')
                return redirect('inventario:producto_detail', pk=producto.pk)
            except Exception as e:
                messages.error(request, f'Error al registrar entrada: {str(e)}')
    else:
        form = MovimientoEntradaForm()
    
    context = {
        'form': form,
        'producto': producto,
        'title': 'Registrar Entrada',
    }
    
    return render(request, 'inventario/movimiento_form.html', context)


@login_required
def salida_inventario(request, pk):
    """Vista para registrar una salida de inventario."""
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        form = MovimientoSalidaForm(request.POST)
        if form.is_valid():
            try:
                movimiento = InventarioService.registrar_salida(
                    producto=producto,
                    cantidad=form.cleaned_data['cantidad'],
                    origen=form.cleaned_data['origen'],
                    documento=form.cleaned_data['documento'],
                    notas=form.cleaned_data['notas'],
                    usuario=request.user
                )
                messages.success(request, 'Salida de inventario registrada correctamente.')
                return redirect('inventario:producto_detail', pk=producto.pk)
            except Exception as e:
                messages.error(request, f'Error al registrar salida: {str(e)}')
    else:
        form = MovimientoSalidaForm()
    
    context = {
        'form': form,
        'producto': producto,
        'title': 'Registrar Salida',
    }
    
    return render(request, 'inventario/movimiento_form.html', context)


@login_required
def categoria_list(request):
    """Vista para listar categorías."""
    categorias = Categoria.objects.filter(activo=True).order_by('nombre')
    
    context = {
        'categorias': categorias,
    }
    
    return render(request, 'inventario/categoria_list.html', context)


@login_required
def categoria_create(request):
    """Vista para crear una categoría."""
    if request.method == 'POST':
        form = CategoriaForm(request.POST, request.FILES)
        if form.is_valid():
            categoria = form.save(commit=False)
            categoria.creado_por = request.user
            categoria.modificado_por = request.user
            categoria.save()
            messages.success(request, 'Categoría creada correctamente.')
            return redirect('inventario:categoria_list')
    else:
        form = CategoriaForm()
    
    context = {
        'form': form,
        'title': 'Crear Categoría',
    }
    
    return render(request, 'inventario/categoria_form.html', context)


@login_required
def categoria_update(request, pk):
    """Vista para actualizar una categoría."""
    categoria = get_object_or_404(Categoria, pk=pk)
    
    if request.method == 'POST':
        form = CategoriaForm(request.POST, request.FILES, instance=categoria)
        if form.is_valid():
            categoria = form.save(commit=False)
            categoria.modificado_por = request.user
            categoria.save()
            messages.success(request, 'Categoría actualizada correctamente.')
            return redirect('inventario:categoria_list')
    else:
        form = CategoriaForm(instance=categoria)
    
    context = {
        'form': form,
        'categoria': categoria,
        'title': 'Editar Categoría',
    }
    
    return render(request, 'inventario/categoria_form.html', context)


@login_required
def proveedor_list(request):
    """Vista para listar proveedores."""
    search_query = request.GET.get('search', '')
    
    proveedores = Proveedor.objects.filter(activo=True)
    
    if search_query:
        proveedores = proveedores.filter(
            Q(nombre__icontains=search_query) | 
            Q(ruc__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    proveedores = proveedores.order_by('nombre')
    
    context = {
        'proveedores': proveedores,
        'search_query': search_query,
    }
    
    return render(request, 'inventario/proveedor_list.html', context)


@login_required
def proveedor_detail(request, pk):
    """Vista para ver detalles de un proveedor."""
    proveedor = get_object_or_404(Proveedor, pk=pk)
    
    context = {
        'proveedor': proveedor,
    }
    
    return render(request, 'inventario/proveedor_detail.html', context)


@login_required
def proveedor_create(request):
    """Vista para crear un proveedor."""
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            proveedor = form.save(commit=False)
            proveedor.creado_por = request.user
            proveedor.modificado_por = request.user
            proveedor.save()
            messages.success(request, 'Proveedor creado correctamente.')
            return redirect('inventario:proveedor_detail', pk=proveedor.pk)
    else:
        form = ProveedorForm()
    
    context = {
        'form': form,
        'title': 'Crear Proveedor',
    }
    
    return render(request, 'inventario/proveedor_form.html', context)


@login_required
def proveedor_update(request, pk):
    """Vista para actualizar un proveedor."""
    proveedor = get_object_or_404(Proveedor, pk=pk)
    
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            proveedor = form.save(commit=False)
            proveedor.modificado_por = request.user
            proveedor.save()
            messages.success(request, 'Proveedor actualizado correctamente.')
            return redirect('inventario:proveedor_detail', pk=proveedor.pk)
    else:
        form = ProveedorForm(instance=proveedor)
    
    context = {
        'form': form,
        'proveedor': proveedor,
        'title': 'Editar Proveedor',
    }
    
    return render(request, 'inventario/proveedor_form.html', context)


@login_required
def movimiento_list(request):
    """Vista para listar movimientos de inventario."""
    tipo = request.GET.get('tipo', '')
    producto_id = request.GET.get('producto', '')
    
    movimientos = MovimientoInventario.objects.all()
    
    if tipo:
        movimientos = movimientos.filter(tipo=tipo)
    
    if producto_id:
        movimientos = movimientos.filter(producto_id=producto_id)
    
    movimientos = movimientos.order_by('-fecha')
    
    # Paginación
    paginator = Paginator(movimientos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'tipo': tipo,
        'producto_id': producto_id,
    }
    
    return render(request, 'inventario/movimiento_list.html', context)