from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.utils import IntegrityError
from datetime import date, timedelta
from decimal import Decimal

from inventario.models import (
    Categoria, Proveedor, Producto, MovimientoInventario,
    Almacen, StockAlmacen, Variacion, Lote, OrdenCompra, ItemOrdenCompra, ContactoProveedor
)

class CategoriaModelTest(TestCase):
    """Pruebas para el modelo Categoria."""

    def test_categoria_creacion(self):
        """Verifica la creación de una categoría."""
        categoria = Categoria.objects.create(
            nombre="Electrónica",
            descripcion="Productos electrónicos",
            codigo="ELEC",
            orden=1
        )
        self.assertEqual(categoria.nombre, "Electrónica")
        self.assertEqual(categoria.descripcion, "Productos electrónicos")
        self.assertEqual(categoria.codigo, "ELEC")
        self.assertEqual(categoria.orden, 1)
        self.assertIsNone(categoria.categoria_padre)
        self.assertTrue(isinstance(categoria, Categoria))

    def test_categoria_str(self):
        """Verifica el método __str__ de Categoria."""
        categoria = Categoria.objects.create(nombre="Electrónica")
        self.assertEqual(str(categoria), "Electrónica")

    def test_categoria_codigo_unico(self):
        """Verifica que el campo codigo sea único."""
        Categoria.objects.create(nombre="Electrónica", codigo="ELEC")
        with self.assertRaises(IntegrityError):
            Categoria.objects.create(nombre="Gadgets", codigo="ELEC")

    def test_categoria_relacion_padre(self):
        """Verifica la relación padre-hijo de Categoria."""
        parent_categoria = Categoria.objects.create(nombre="Electrónica")
        child_categoria = Categoria.objects.create(
            nombre="Televisores",
            categoria_padre=parent_categoria
        )
        self.assertEqual(child_categoria.categoria_padre, parent_categoria)
        self.assertIn(child_categoria, parent_categoria.subcategorias.all())

    def test_categoria_ruta_completa(self):
        """Verifica la propiedad ruta_completa de Categoria."""
        parent1 = Categoria.objects.create(nombre="Electrónica")
        parent2 = Categoria.objects.create(
            nombre="Televisores",
            categoria_padre=parent1
        )
        child = Categoria.objects.create(
            nombre="Smart TVs",
            categoria_padre=parent2
        )
        self.assertEqual(parent1.ruta_completa, "Electrónica")
        self.assertEqual(parent2.ruta_completa, "Electrónica > Televisores")
        self.assertEqual(child.ruta_completa, "Electrónica > Televisores > Smart TVs")

    def test_categoria_ordenamiento(self):
        """Verifica el ordenamiento de categorías por orden y nombre."""
        categoria1 = Categoria.objects.create(nombre="Zapatillas", orden=2)
        categoria2 = Categoria.objects.create(nombre="Camisetas", orden=1)
        categoria3 = Categoria.objects.create(nombre="Accesorios", orden=1)
        categorias = Categoria.objects.all()
        self.assertEqual(categorias[0].nombre, "Accesorios")
        self.assertEqual(categorias[1].nombre, "Camisetas")
        self.assertEqual(categorias[2].nombre, "Zapatillas")

    def test_categoria_no_ciclo(self):
        """Verifica que una categoría no pueda ser su propio padre."""
        categoria = Categoria.objects.create(nombre="Electrónica")
        categoria.categoria_padre = categoria
        with self.assertRaisesMessage(ValidationError, 'Una categoría no puede ser su propio padre.'):
            categoria.full_clean()

    def test_categoria_orden_no_negativo(self):
        """Verifica que el orden no sea negativo."""
        with self.assertRaisesMessage(ValidationError, 'El orden no puede ser negativo.'):
            categoria = Categoria(nombre="Electrónica", orden=-1)
            categoria.full_clean()

    # Nuevos tests
    def test_categoria_imagen_opcional(self):
        """Verifica que el campo imagen pueda ser nulo."""
        categoria = Categoria.objects.create(nombre="Electrónica", imagen=None)
        self.assertIsNone(categoria.imagen)

    def test_categoria_nombre_max_length(self):
        """Verifica la longitud máxima del campo nombre."""
        with self.assertRaises(ValidationError):
            categoria = Categoria(nombre="A" * 101)
            categoria.full_clean()

    def test_categoria_codigo_max_length(self):
        """Verifica la longitud máxima del campo codigo."""
        with self.assertRaises(ValidationError):
            categoria = Categoria(nombre="Electrónica", codigo="A" * 21)
            categoria.full_clean()

class ProveedorModelTest(TestCase):
    """Pruebas para el modelo Proveedor."""

    def test_proveedor_creacion(self):
        """Verifica la creación de un proveedor."""
        proveedor = Proveedor.objects.create(
            nombre="Tech Supplier",
            ruc="1234567890001",
            direccion="Av. Principal 123",
            telefono="0991234567",
            email="contacto@techsupplier.com",
            dias_credito=30,
            limite_credito=Decimal('5000.00'),
            estado='activo'
        )
        self.assertEqual(proveedor.nombre, "Tech Supplier")
        self.assertEqual(proveedor.ruc, "1234567890001")
        self.assertEqual(proveedor.direccion, "Av. Principal 123")
        self.assertEqual(proveedor.telefono, "0991234567")
        self.assertEqual(proveedor.email, "contacto@techsupplier.com")
        self.assertEqual(proveedor.dias_credito, 30)
        self.assertEqual(proveedor.limite_credito, Decimal('5000.00'))
        self.assertEqual(proveedor.estado, 'activo')
        self.assertTrue(isinstance(proveedor, Proveedor))

    def test_proveedor_str(self):
        """Verifica el método __str__ de Proveedor."""
        proveedor = Proveedor.objects.create(nombre="Tech Supplier", ruc="1234567890001")
        self.assertEqual(str(proveedor), "Tech Supplier")

    def test_proveedor_ruc_unico(self):
        """Verifica que el campo ruc sea único."""
        Proveedor.objects.create(nombre="Tech Supplier", ruc="1234567890001")
        with self.assertRaises(IntegrityError):
            Proveedor.objects.create(nombre="Other Supplier", ruc="1234567890001")

    def test_proveedor_limite_credito_no_negativo(self):
        """Verifica que el límite de crédito no sea negativo."""
        with self.assertRaisesMessage(ValidationError, 'El límite de crédito no puede ser negativo.'):
            proveedor = Proveedor(
                nombre="Tech Supplier",
                ruc="9876543210001",
                limite_credito=Decimal('-1000.00')
            )
            proveedor.full_clean()

    # Nuevos tests
    def test_proveedor_campos_opcionales(self):
        """Verifica que los campos opcionales puedan estar vacíos."""
        proveedor = Proveedor.objects.create(
            nombre="Tech Supplier",
            ruc="1234567890001",
            direccion="",
            telefono="",
            email="",
            sitio_web="",
            notas=""
        )
        self.assertEqual(proveedor.direccion, "")
        self.assertEqual(proveedor.telefono, "")
        self.assertEqual(proveedor.email, "")
        self.assertEqual(proveedor.sitio_web, "")
        self.assertEqual(proveedor.notas, "")

    def test_proveedor_ruc_max_length(self):
        """Verifica la longitud máxima del campo ruc."""
        with self.assertRaises(ValidationError):
            proveedor = Proveedor(nombre="Tech Supplier", ruc="A" * 14)
            proveedor.full_clean()

    def test_proveedor_estado_choices(self):
        """Verifica los valores posibles del campo estado."""
        proveedor_activo = Proveedor.objects.create(nombre="Supplier1", ruc="1234567890001", estado='activo')
        proveedor_inactivo = Proveedor.objects.create(nombre="Supplier2", ruc="9876543210001", estado='inactivo')
        self.assertEqual(proveedor_activo.estado, 'activo')
        self.assertEqual(proveedor_inactivo.estado, 'inactivo')

class ContactoProveedorModelTest(TestCase):
    """Pruebas para el modelo ContactoProveedor."""

    def setUp(self):
        self.proveedor = Proveedor.objects.create(
            nombre="Tech Supplier",
            ruc="1234567890001"
        )

    def test_contacto_creacion(self):
        """Verifica la creación de un contacto de proveedor."""
        contacto = ContactoProveedor.objects.create(
            proveedor=self.proveedor,
            nombre="Ana Lopez",
            telefono="0991234567",
            email="ana@techsupplier.com",
            cargo="Gerente de Ventas"
        )
        self.assertEqual(contacto.proveedor, self.proveedor)
        self.assertEqual(contacto.nombre, "Ana Lopez")
        self.assertEqual(contacto.telefono, "0991234567")
        self.assertEqual(contacto.email, "ana@techsupplier.com")
        self.assertEqual(contacto.cargo, "Gerente de Ventas")
        self.assertTrue(isinstance(contacto, ContactoProveedor))

    def test_contacto_str(self):
        """Verifica el método __str__ de ContactoProveedor."""
        contacto = ContactoProveedor.objects.create(
            proveedor=self.proveedor,
            nombre="Ana Lopez"
        )
        self.assertEqual(str(contacto), f"Ana Lopez ({self.proveedor})")

    def test_contacto_relacion(self):
        """Verifica la relación con Proveedor."""
        contacto = ContactoProveedor.objects.create(
            proveedor=self.proveedor,
            nombre="Ana Lopez"
        )
        self.assertEqual(contacto.proveedor, self.proveedor)
        self.assertIn(contacto, self.proveedor.contactos.all())

    # Nuevos tests
    def test_contacto_campos_opcionales(self):
        """Verifica que los campos opcionales puedan estar vacíos."""
        contacto = ContactoProveedor.objects.create(
            proveedor=self.proveedor,
            nombre="Ana Lopez",
            telefono="",
            email="",
            cargo=""
        )
        self.assertEqual(contacto.telefono, "")
        self.assertEqual(contacto.email, "")
        self.assertEqual(contacto.cargo, "")

    def test_contacto_cascade_deletion(self):
        """Verifica que se eliminen los contactos al eliminar el proveedor."""
        contacto = ContactoProveedor.objects.create(
            proveedor=self.proveedor,
            nombre="Ana Lopez"
        )
        self.proveedor.delete()
        self.assertFalse(ContactoProveedor.objects.filter(id=contacto.id).exists())

    def test_contacto_nombre_max_length(self):
        """Verifica la longitud máxima del campo nombre."""
        with self.assertRaises(ValidationError):
            contacto = ContactoProveedor(proveedor=self.proveedor, nombre="A" * 101)
            contacto.full_clean()

class AlmacenModelTest(TestCase):
    """Pruebas para el modelo Almacen."""

    def test_almacen_creacion(self):
        """Verifica la creación de un almacén."""
        almacen = Almacen.objects.create(
            nombre="Bodega Principal",
            direccion="Av. Central 456",
            responsable="Luis Garcia",
            activo=True
        )
        self.assertEqual(almacen.nombre, "Bodega Principal")
        self.assertEqual(almacen.direccion, "Av. Central 456")
        self.assertEqual(almacen.responsable, "Luis Garcia")
        self.assertTrue(almacen.activo)
        self.assertTrue(isinstance(almacen, Almacen))

    def test_almacen_str(self):
        """Verifica el método __str__ de Almacen."""
        almacen = Almacen.objects.create(nombre="Bodega Principal")
        self.assertEqual(str(almacen), "Bodega Principal")

    # Nuevos tests
    def test_almacen_campos_opcionales(self):
        """Verifica que los campos opcionales puedan estar vacíos."""
        almacen = Almacen.objects.create(
            nombre="Bodega Principal",
            direccion="",
            responsable=""
        )
        self.assertEqual(almacen.direccion, "")
        self.assertEqual(almacen.responsable, "")

    def test_almacen_activo_false(self):
        """Verifica el campo activo con valor False."""
        almacen = Almacen.objects.create(nombre="Bodega Inactiva", activo=False)
        self.assertFalse(almacen.activo)

    def test_almacen_nombre_max_length(self):
        """Verifica la longitud máxima del campo nombre."""
        with self.assertRaises(ValidationError):
            almacen = Almacen(nombre="A" * 101)
            almacen.full_clean()

class StockAlmacenModelTest(TestCase):
    """Pruebas para el modelo StockAlmacen."""

    def setUp(self):
        self.categoria = Categoria.objects.create(nombre="Electrónica")
        self.producto = Producto.objects.create(
            codigo="TV001",
            nombre="Smart TV 55\"",
            categoria=self.categoria,
            precio_venta=Decimal('600.00'),
            stock=Decimal('0.00')
        )
        self.almacen = Almacen.objects.create(nombre="Bodega Principal")

    def test_stock_almacen_creacion(self):
        """Verifica la creación de un stock por almacén."""
        stock = StockAlmacen.objects.create(
            producto=self.producto,
            almacen=self.almacen,
            cantidad=Decimal('10.00')
        )
        self.assertEqual(stock.producto, self.producto)
        self.assertEqual(stock.almacen, self.almacen)
        self.assertEqual(stock.cantidad, Decimal('10.00'))
        self.assertTrue(isinstance(stock, StockAlmacen))

    def test_stock_almacen_str(self):
        """Verifica el método __str__ de StockAlmacen."""
        stock = StockAlmacen.objects.create(
            producto=self.producto,
            almacen=self.almacen,
            cantidad=Decimal('10.00')
        )
        self.assertEqual(str(stock), f"{self.producto} - {self.almacen} - 10.00")

    def test_stock_almacen_unico(self):
        """Verifica que la combinación producto-almacén sea única."""
        StockAlmacen.objects.create(
            producto=self.producto,
            almacen=self.almacen,
            cantidad=Decimal('10.00')
        )
        with self.assertRaises(IntegrityError):
            StockAlmacen.objects.create(
                producto=self.producto,
                almacen=self.almacen,
                cantidad=Decimal('5.00')
            )

    def test_stock_almacen_cantidad_no_negativa(self):
        """Verifica que la cantidad no sea negativa."""
        with self.assertRaisesMessage(ValidationError, 'La cantidad no puede ser negativa.'):
            stock = StockAlmacen(
                producto=self.producto,
                almacen=self.almacen,
                cantidad=Decimal('-5.00')
            )
            stock.full_clean()

    # Nuevos tests
    def test_stock_almacen_cascade_deletion(self):
        """Verifica que se elimine el stock al eliminar producto o almacén."""
        stock = StockAlmacen.objects.create(
            producto=self.producto,
            almacen=self.almacen,
            cantidad=Decimal('10.00')
        )
        self.producto.delete()
        self.assertFalse(StockAlmacen.objects.filter(id=stock.id).exists())
        # Re-crear para probar eliminación de almacén
        self.producto = Producto.objects.create(
            codigo="TV002",
            nombre="Smart TV 65\"",
            categoria=self.categoria,
            precio_venta=Decimal('800.00')
        )
        stock = StockAlmacen.objects.create(
            producto=self.producto,
            almacen=self.almacen,
            cantidad=Decimal('10.00')
        )
        self.almacen.delete()
        self.assertFalse(StockAlmacen.objects.filter(id=stock.id).exists())

    def test_stock_almacen_cantidad_precision(self):
        """Verifica la precisión del campo cantidad."""
        stock = StockAlmacen.objects.create(
            producto=self.producto,
            almacen=self.almacen,
            cantidad=Decimal('99999999.99')
        )
        self.assertEqual(stock.cantidad, Decimal('99999999.99'))
        with self.assertRaises(ValidationError):
            stock.cantidad = Decimal('100000000.00')  # Excede max_digits
            stock.full_clean()

class VariacionModelTest(TestCase):
    """Pruebas para el modelo Variacion."""

    def setUp(self):
        self.categoria = Categoria.objects.create(nombre="Ropa")
        self.producto = Producto.objects.create(
            codigo="CAM001",
            nombre="Camiseta",
            categoria=self.categoria,
            precio_venta=Decimal('20.00'),
            stock=Decimal('0.00')
        )

    def test_variacion_creacion(self):
        """Verifica la creación de una variación."""
        variacion = Variacion.objects.create(
            producto=self.producto,
            atributo="Color: Azul, Talla: M",
            codigo="CAM001-AZUL-M",
            stock=Decimal('5.00'),
            precio_venta=Decimal('22.00')
        )
        self.assertEqual(variacion.producto, self.producto)
        self.assertEqual(variacion.atributo, "Color: Azul, Talla: M")
        self.assertEqual(variacion.codigo, "CAM001-AZUL-M")
        self.assertEqual(variacion.stock, Decimal('5.00'))
        self.assertEqual(variacion.precio_venta, Decimal('22.00'))
        self.assertTrue(isinstance(variacion, Variacion))

    def test_variacion_str(self):
        """Verifica el método __str__ de Variacion."""
        variacion = Variacion.objects.create(
            producto=self.producto,
            atributo="Color: Azul, Talla: M",
            codigo="CAM001-AZUL-M",
            precio_venta=Decimal('22.00')
        )
        self.assertEqual(str(variacion), f"{self.producto} - Color: Azul, Talla: M")

    def test_variacion_codigo_unico(self):
        """Verifica que el campo codigo sea único."""
        Variacion.objects.create(
            producto=self.producto,
            atributo="Color: Azul, Talla: M",
            codigo="CAM001-AZUL-M",
            precio_venta=Decimal('22.00')
        )
        with self.assertRaises(IntegrityError):
            Variacion.objects.create(
                producto=self.producto,
                atributo="Color: Rojo, Talla: L",
                codigo="CAM001-AZUL-M",
                precio_venta=Decimal('23.00')
            )

    def test_variacion_valores_no_negativos(self):
        """Verifica que el stock y el precio no sean negativos."""
        with self.assertRaisesMessage(ValidationError, 'El stock no puede ser negativo.'):
            variacion = Variacion(
                producto=self.producto,
                atributo="Color: Azul, Talla: M",
                codigo="CAM001-AZUL-M",
                stock=Decimal('-5.00'),
                precio_venta=Decimal('22.00')
            )
            variacion.full_clean()

        with self.assertRaisesMessage(ValidationError, 'El precio de venta no puede ser negativo.'):
            variacion = Variacion(
                producto=self.producto,
                atributo="Color: Azul, Talla: M",
                codigo="CAM001-AZUL-M",
                stock=Decimal('5.00'),
                precio_venta=Decimal('-22.00')
            )
            variacion.full_clean()

    def test_variacion_sincroniza_stock(self):
        """Verifica que el stock del producto se sincronice con las variaciones."""
        variacion1 = Variacion.objects.create(
            producto=self.producto,
            atributo="Color: Azul, Talla: M",
            codigo="CAM001-AZUL-M",
            stock=Decimal('5.00'),
            precio_venta=Decimal('22.00')
        )
        variacion2 = Variacion.objects.create(
            producto=self.producto,
            atributo="Color: Rojo, Talla: L",
            codigo="CAM001-ROJO-L",
            stock=Decimal('3.00'),
            precio_venta=Decimal('23.00')
        )
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, Decimal('8.00'))  # 5 + 3

    # Nuevos tests
    def test_variacion_imagen_opcional(self):
        """Verifica que el campo imagen pueda ser nulo."""
        variacion = Variacion.objects.create(
            producto=self.producto,
            atributo="Color: Azul, Talla: M",
            codigo="CAM001-AZUL-M",
            precio_venta=Decimal('22.00'),
            imagen=None
        )
        self.assertIsNone(variacion.imagen)

    def test_variacion_atributo_max_length(self):
        """Verifica la longitud máxima del campo atributo."""
        with self.assertRaises(ValidationError):
            variacion = Variacion(
                producto=self.producto,
                atributo="A" * 101,
                codigo="CAM001-AZUL-M",
                precio_venta=Decimal('22.00')
            )
            variacion.full_clean()

    def test_variacion_cascade_deletion(self):
        """Verifica que se eliminen las variaciones al eliminar el producto."""
        variacion = Variacion.objects.create(
            producto=self.producto,
            atributo="Color: Azul, Talla: M",
            codigo="CAM001-AZUL-M",
            precio_venta=Decimal('22.00')
        )
        self.producto.delete()
        self.assertFalse(Variacion.objects.filter(id=variacion.id).exists())

class LoteModelTest(TestCase):
    """Pruebas para el modelo Lote."""

    def setUp(self):
        self.categoria = Categoria.objects.create(nombre="Alimentos")
        self.producto = Producto.objects.create(
            codigo="LECHE001",
            nombre="Leche Entera",
            categoria=self.categoria,
            precio_venta=Decimal('2.00'),
            stock=Decimal('0.00')
        )
        self.almacen = Almacen.objects.create(nombre="Bodega Principal")

    def test_lote_creacion(self):
        """Verifica la creación de un lote."""
        lote = Lote.objects.create(
            producto=self.producto,
            numero_lote="LOTE2023-001",
            fecha_vencimiento=date.today() + timedelta(days=365),
            fecha_produccion=date.today(),
            cantidad=Decimal('100.00'),
            almacen=self.almacen
        )
        self.assertEqual(lote.producto, self.producto)
        self.assertEqual(lote.numero_lote, "LOTE2023-001")
        self.assertEqual(lote.fecha_vencimiento, date.today() + timedelta(days=365))
        self.assertEqual(lote.fecha_produccion, date.today())
        self.assertEqual(lote.cantidad, Decimal('100.00'))
        self.assertEqual(lote.almacen, self.almacen)
        self.assertTrue(isinstance(lote, Lote))

    def test_lote_str(self):
        """Verifica el método __str__ de Lote."""
        lote = Lote.objects.create(
            producto=self.producto,
            numero_lote="LOTE2023-001",
            cantidad=Decimal('100.00'),
            almacen=self.almacen
        )
        self.assertEqual(str(lote), f"{self.producto} - Lote LOTE2023-001")

    def test_lote_cantidad_no_negativa(self):
        """Verifica que la cantidad no sea negativa."""
        with self.assertRaisesMessage(ValidationError, 'La cantidad no puede ser negativa.'):
            lote = Lote(
                producto=self.producto,
                numero_lote="LOTE2023-001",
                cantidad=Decimal('-100.00'),
                almacen=self.almacen
            )
            lote.full_clean()

    def test_lote_fechas_validas(self):
        """Verifica que la fecha de vencimiento no sea anterior a la fecha de producción."""
        with self.assertRaisesMessage(ValidationError, 'La fecha de vencimiento no puede ser anterior a la fecha de producción.'):
            lote = Lote(
                producto=self.producto,
                numero_lote="LOTE2023-001",
                fecha_vencimiento=date.today(),
                fecha_produccion=date.today() + timedelta(days=1),
                cantidad=Decimal('100.00'),
                almacen=self.almacen
            )
            lote.full_clean()

    # Nuevos tests
    def test_lote_fechas_opcionales(self):
        """Verifica que las fechas puedan ser nulas."""
        lote = Lote.objects.create(
            producto=self.producto,
            numero_lote="LOTE2023-001",
            cantidad=Decimal('100.00'),
            almacen=self.almacen,
            fecha_vencimiento=None,
            fecha_produccion=None
        )
        self.assertIsNone(lote.fecha_vencimiento)
        self.assertIsNone(lote.fecha_produccion)

    def test_lote_numero_lote_max_length(self):
        """Verifica la longitud máxima del campo numero_lote."""
        with self.assertRaises(ValidationError):
            lote = Lote(
                producto=self.producto,
                numero_lote="A" * 51,
                cantidad=Decimal('100.00'),
                almacen=self.almacen
            )
            lote.full_clean()

    def test_lote_protect_deletion(self):
        """Verifica que no se pueda eliminar un producto o almacén con lotes asociados."""
        lote = Lote.objects.create(
            producto=self.producto,
            numero_lote="LOTE2023-001",
            cantidad=Decimal('100.00'),
            almacen=self.almacen
        )
        with self.assertRaises(IntegrityError):
            self.producto.delete()
        with self.assertRaises(IntegrityError):
            self.almacen.delete()

class OrdenCompraModelTest(TestCase):
    """Pruebas para los modelos OrdenCompra e ItemOrdenCompra."""

    def setUp(self):
        self.proveedor = Proveedor.objects.create(
            nombre="Tech Supplier",
            ruc="1234567890001"
        )
        self.categoria = Categoria.objects.create(nombre="Electrónica")
        self.producto = Producto.objects.create(
            codigo="TV001",
            nombre="Smart TV 55\"",
            categoria=self.categoria,
            precio_venta=Decimal('600.00')
        )

    def test_orden_compra_creacion(self):
        """Verifica la creación de una orden de compra."""
        orden = OrdenCompra.objects.create(
            proveedor=self.proveedor,
            numero="OC001",
            fecha=date.today(),
            estado='pendiente',
            total=Decimal('0.00')
        )
        self.assertEqual(orden.proveedor, self.proveedor)
        self.assertEqual(orden.numero, "OC001")
        self.assertEqual(orden.fecha, date.today())
        self.assertEqual(orden.estado, 'pendiente')
        self.assertEqual(orden.total, Decimal('0.00'))
        self.assertTrue(isinstance(orden, OrdenCompra))

    def test_orden_compra_str(self):
        """Verifica el método __str__ de OrdenCompra."""
        orden = OrdenCompra.objects.create(
            proveedor=self.proveedor,
            numero="OC001",
            fecha=date.today()
        )
        self.assertEqual(str(orden), f"Orden OC001 - {self.proveedor}")

    def test_orden_compra_numero_unico(self):
        """Verifica que el campo numero sea único."""
        OrdenCompra.objects.create(
            proveedor=self.proveedor,
            numero="OC001",
            fecha=date.today()
        )
        with self.assertRaises(IntegrityError):
            OrdenCompra.objects.create(
                proveedor=self.proveedor,
                numero="OC001",
                fecha=date.today()
            )

    def test_orden_compra_total_no_negativo(self):
        """Verifica que el total no sea negativo."""
        with self.assertRaisesMessage(ValidationError, 'El total no puede ser negativo.'):
            orden = OrdenCompra(
                proveedor=self.proveedor,
                numero="OC001",
                fecha=date.today(),
                total=Decimal('-100.00')
            )
            orden.full_clean()

    def test_item_orden_compra_creacion(self):
        """Verifica la creación de un ítem de orden de compra."""
        orden = OrdenCompra.objects.create(
            proveedor=self.proveedor,
            numero="OC001",
            fecha=date.today()
        )
        item = ItemOrdenCompra.objects.create(
            orden_compra=orden,
            producto=self.producto,
            cantidad=Decimal('5.00'),
            precio_unitario=Decimal('500.00')
        )
        self.assertEqual(item.orden_compra, orden)
        self.assertEqual(item.producto, self.producto)
        self.assertEqual(item.cantidad, Decimal('5.00'))
        self.assertEqual(item.precio_unitario, Decimal('500.00'))
        self.assertEqual(item.subtotal, Decimal('2500.00'))  # 5 * 500
        self.assertTrue(isinstance(item, ItemOrdenCompra))

    def test_item_orden_compra_str(self):
        """Verifica el método __str__ de ItemOrdenCompra."""
        orden = OrdenCompra.objects.create(
            proveedor=self.proveedor,
            numero="OC001",
            fecha=date.today()
        )
        item = ItemOrdenCompra.objects.create(
            orden_compra=orden,
            producto=self.producto,
            cantidad=Decimal('5.00'),
            precio_unitario=Decimal('500.00')
        )
        self.assertEqual(str(item), f"{self.producto} - 5.00")

    def test_item_orden_compra_calculo_subtotal(self):
        """Verifica el cálculo automático del subtotal."""
        orden = OrdenCompra.objects.create(
            proveedor=self.proveedor,
            numero="OC001",
            fecha=date.today()
        )
        item = ItemOrdenCompra.objects.create(
            orden_compra=orden,
            producto=self.producto,
            cantidad=Decimal('5.00'),
            precio_unitario=Decimal('500.00')
        )
        self.assertEqual(item.subtotal, Decimal('2500.00'))
        item.cantidad = Decimal('10.00')
        item.save()
        self.assertEqual(item.subtotal, Decimal('5000.00'))  # 10 * 500
        orden.refresh_from_db()
        self.assertEqual(orden.total, Decimal('5000.00'))

    def test_item_orden_compra_valores_no_negativos(self):
        """Verifica que la cantidad y el precio unitario no sean negativos."""
        orden = OrdenCompra.objects.create(
            proveedor=self.proveedor,
            numero="OC001",
            fecha=date.today()
        )
        with self.assertRaisesMessage(ValidationError, 'La cantidad no puede ser negativa.'):
            item = ItemOrdenCompra(
                orden_compra=orden,
                producto=self.producto,
                cantidad=Decimal('-5.00'),
                precio_unitario=Decimal('500.00')
            )
            item.full_clean()

        with self.assertRaisesMessage(ValidationError, 'El precio unitario no puede ser negativo.'):
            item = ItemOrdenCompra(
                orden_compra=orden,
                producto=self.producto,
                cantidad=Decimal('5.00'),
                precio_unitario=Decimal('-500.00')
            )
            item.full_clean()

    # Nuevos tests
    def test_orden_compra_estado_transiciones(self):
        """Verifica las transiciones de estado."""
        orden = OrdenCompra.objects.create(
            proveedor=self.proveedor,
            numero="OC001",
            fecha=date.today(),
            estado='pendiente'
        )
        orden.estado = 'completada'
        orden.save()
        self.assertEqual(orden.estado, 'completada')
        orden.estado = 'cancelada'
        orden.save()
        self.assertEqual(orden.estado, 'cancelada')

    def test_item_orden_compra_cascade_deletion(self):
        """Verifica que se eliminen los ítems al eliminar la orden."""
        orden = OrdenCompra.objects.create(
            proveedor=self.proveedor,
            numero="OC001",
            fecha=date.today()
        )
        item = ItemOrdenCompra.objects.create(
            orden_compra=orden,
            producto=self.producto,
            cantidad=Decimal('5.00'),
            precio_unitario=Decimal('500.00')
        )
        orden.delete()
        self.assertFalse(ItemOrdenCompra.objects.filter(id=item.id).exists())

    def test_orden_compra_protect_deletion(self):
        """Verifica que no se pueda eliminar un proveedor con órdenes asociadas."""
        orden = OrdenCompra.objects.create(
            proveedor=self.proveedor,
            numero="OC001",
            fecha=date.today()
        )
        with self.assertRaises(IntegrityError):
            self.proveedor.delete()

class ProductoModelTest(TestCase):
    """Pruebas para el modelo Producto."""

    def setUp(self):
        self.categoria = Categoria.objects.create(nombre="Electrónica")
        self.proveedor = Proveedor.objects.create(
            nombre="Tech Supplier",
            ruc="1234567890001"
        )

    def test_producto_creacion(self):
        """Verifica la creación de un producto."""
        producto = Producto.objects.create(
            codigo="TV001",
            nombre="Smart TV 55\"",
            descripcion="Televisor LED 4K",
            precio_compra=Decimal('400.00'),
            precio_venta=Decimal('600.00'),
            stock=Decimal('10.00'),
            stock_minimo=Decimal('2.00'),
            categoria=self.categoria,
            iva=Decimal('12.00'),
            es_inventariable=True,
            mostrar_en_tienda=True,
            destacado=True
        )
        producto.proveedores.add(self.proveedor)
        self.assertEqual(producto.codigo, "TV001")
        self.assertEqual(producto.nombre, "Smart TV 55\"")
        self.assertEqual(producto.descripcion, "Televisor LED 4K")
        self.assertEqual(producto.precio_compra, Decimal('400.00'))
        self.assertEqual(producto.precio_venta, Decimal('600.00'))
        self.assertEqual(producto.stock, Decimal('10.00'))
        self.assertEqual(producto.stock_minimo, Decimal('2.00'))
        self.assertEqual(producto.categoria, self.categoria)
        self.assertEqual(producto.iva, Decimal('12.00'))
        self.assertTrue(producto.es_inventariable)
        self.assertTrue(producto.mostrar_en_tienda)
        self.assertTrue(producto.destacado)
        self.assertEqual(producto.url_slug, "smart-tv-55")
        self.assertIn(self.proveedor, producto.proveedores.all())
        self.assertTrue(isinstance(producto, Producto))

    def test_producto_str(self):
        """Verifica el método __str__ de Producto."""
        producto = Producto.objects.create(
            codigo="TV001",
            nombre="Smart TV 55\"",
            categoria=self.categoria,
            precio_venta=Decimal('600.00')
        )
        self.assertEqual(str(producto), "TV001 - Smart TV 55\"")

    def test_producto_codigo_unico(self):
        """Verifica que el campo codigo sea único."""
        Producto.objects.create(
            codigo="TV001",
            nombre="Smart TV 55\"",
            categoria=self.categoria,
            precio_venta=Decimal('600.00')
        )
        with self.assertRaises(IntegrityError):
            Producto.objects.create(
                codigo="TV001",
                nombre="Smart TV 65\"",
                categoria=self.categoria,
                precio_venta=Decimal('800.00')
            )

    def test_producto_disponible(self):
        """Verifica la propiedad disponible de Producto."""
        producto_activo = Producto.objects.create(
            codigo="TV001",
            nombre="Smart TV 55\"",
            categoria=self.categoria,
            precio_venta=Decimal('600.00'),
            stock=Decimal('5.00'),
            estado='activo',
            es_inventariable=True
        )
        self.assertTrue(producto_activo.disponible)

        producto_inactivo = Producto.objects.create(
            codigo="TV002",
            nombre="Smart TV 65\"",
            categoria=self.categoria,
            precio_venta=Decimal('800.00'),
            stock=Decimal('5.00'),
            estado='inactivo',
            es_inventariable=True
        )
        self.assertFalse(producto_inactivo.disponible)

        producto_sin_stock = Producto.objects.create(
            codigo="TV003",
            nombre="Smart TV 75\"",
            categoria=self.categoria,
            precio_venta=Decimal('1000.00'),
            stock=Decimal('0.00'),
            estado='activo',
            es_inventariable=True
        )
        self.assertFalse(producto_sin_stock.disponible)

        producto_no_inventariable = Producto.objects.create(
            codigo="SERV001",
            nombre="Servicio Técnico",
            categoria=self.categoria,
            precio_venta=Decimal('100.00'),
            stock=Decimal('0.00'),
            estado='activo',
            es_inventariable=False
        )
        self.assertTrue(producto_no_inventariable.disponible)

    def test_producto_margen(self):
        """Verifica la propiedad margen de Producto."""
        producto = Producto.objects.create(
            codigo="TV001",
            nombre="Smart TV 55\"",
            categoria=self.categoria,
            precio_compra=Decimal('400.00'),
            precio_venta=Decimal('600.00')
        )
        self.assertEqual(producto.margen, Decimal('50.0'))  # (600 - 400) / 400 * 100

        producto_sin_compra = Producto.objects.create(
            codigo="TV002",
            nombre="Smart TV 65\"",
            categoria=self.categoria,
            precio_compra=Decimal('0.00'),
            precio_venta=Decimal('800.00')
        )
        self.assertEqual(producto_sin_compra.margen, Decimal('0.0'))

    def test_producto_url_slug(self):
        """Verifica la generación automática del url_slug."""
        producto = Producto.objects.create(
            codigo="TV001",
            nombre="Smart TV 55\"",
            categoria=self.categoria,
            precio_venta=Decimal('600.00')
        )
        self.assertEqual(producto.url_slug, "smart-tv-55")

    def test_producto_valores_no_negativos(self):
        """Verifica que los precios, IVA, stock y stock mínimo no sean negativos."""
        for field, error_msg in [
            ('precio_compra', 'El precio de compra no puede ser negativo.'),
            ('precio_venta', 'El precio de venta no puede ser negativo.'),
            ('iva', 'El IVA no puede ser negativo.'),
            ('stock', 'El stock no puede ser negativo.'),
            ('stock_minimo', 'El stock mínimo no puede ser negativo.')
        ]:
            with self.assertRaisesMessage(ValidationError, error_msg):
                producto = Producto(
                    codigo="TV001",
                    nombre="Smart TV 55\"",
                    categoria=self.categoria,
                    precio_venta=Decimal('600.00'),
                    **{field: Decimal('-1.00')}
                )
                producto.full_clean()

    # Nuevos tests
    def test_producto_imagen_opcional(self):
        """Verifica que el campo imagen pueda ser nulo."""
        producto = Producto.objects.create(
            codigo="TV001",
            nombre="Smart TV 55\"",
            categoria=self.categoria,
            precio_venta=Decimal('600.00'),
            imagen=None
        )
        self.assertIsNone(producto.imagen)

    def test_producto_proveedores_multiple(self):
        """Verifica la relación many-to-many con proveedores."""
        proveedor2 = Proveedor.objects.create(nombre="Supplier2", ruc="9876543210001")
        producto = Producto.objects.create(
            codigo="TV001",
            nombre="Smart TV 55\"",
            categoria=self.categoria,
            precio_venta=Decimal('600.00')
        )
        producto.proveedores.add(self.proveedor, proveedor2)
        self.assertEqual(producto.proveedores.count(), 2)
        producto.proveedores.remove(self.proveedor)
        self.assertEqual(producto.proveedores.count(), 1)

    def test_producto_estado_y_tipo_choices(self):
        """Verifica los valores posibles de estado y tipo."""
        producto_activo = Producto.objects.create(
            codigo="TV001",
            nombre="Smart TV 55\"",
            categoria=self.categoria,
            precio_venta=Decimal('600.00'),
            estado='activo',
            tipo='producto'
        )
        producto_inactivo = Producto.objects.create(
            codigo="TV002",
            nombre="Smart TV 65\"",
            categoria=self.categoria,
            precio_venta=Decimal('800.00'),
            estado='inactivo',
            tipo='servicio'
        )
        self.assertEqual(producto_activo.estado, 'activo')
        self.assertEqual(producto_activo.tipo, 'producto')
        self.assertEqual(producto_inactivo.estado, 'inactivo')
        self.assertEqual(producto_inactivo.tipo, 'servicio')

    def test_producto_codigo_max_length(self):
        """Verifica la longitud máxima del campo codigo."""
        with self.assertRaises(ValidationError):
            producto = Producto(
                codigo="A" * 51,
                nombre="Smart TV 55\"",
                categoria=self.categoria,
                precio_venta=Decimal('600.00')
            )
            producto.full_clean()

class MovimientoInventarioModelTest(TestCase):
    """Pruebas para el modelo MovimientoInventario."""

    def setUp(self):
        self.categoria = Categoria.objects.create(nombre="Electrónica")
        self.proveedor = Proveedor.objects.create(
            nombre="Tech Supplier",
            ruc="1234567890001"
        )
        self.producto = Producto.objects.create(
            codigo="TV001",
            nombre="Smart TV 55\"",
            categoria=self.categoria,
            precio_venta=Decimal('600.00'),
            stock=Decimal('10.00'),
            es_inventariable=True
        )
        self.almacen = Almacen.objects.create(nombre="Bodega Principal")
        self.stock_almacen = StockAlmacen.objects.create(
            producto=self.producto,
            almacen=self.almacen,
            cantidad=Decimal('10.00')
        )
        self.lote = Lote.objects.create(
            producto=self.producto,
            numero_lote="LOTE2023-001",
            cantidad=Decimal('10.00'),
            almacen=self.almacen
        )

    def test_movimiento_creacion(self):
        """Verifica la creación de un movimiento de inventario."""
        movimiento = MovimientoInventario.objects.create(
            tipo='entrada',
            origen='compra',
            producto=self.producto,
            cantidad=Decimal('5.00'),
            stock_anterior=Decimal('10.00'),
            stock_nuevo=Decimal('15.00'),
            costo_unitario=Decimal('400.00'),
            proveedor=self.proveedor,
            almacen=self.almacen,
            lote=self.lote,
            documento="FACT001",
            notas="Compra de inventario"
        )
        self.assertEqual(movimiento.tipo, 'entrada')
        self.assertEqual(movimiento.origen, 'compra')
        self.assertEqual(movimiento.producto, self.producto)
        self.assertEqual(movimiento.cantidad, Decimal('5.00'))
        self.assertEqual(movimiento.stock_anterior, Decimal('10.00'))
        self.assertEqual(movimiento.stock_nuevo, Decimal('15.00'))
        self.assertEqual(movimiento.costo_unitario, Decimal('400.00'))
        self.assertEqual(movimiento.proveedor, self.proveedor)
        self.assertEqual(movimiento.almacen, self.almacen)
        self.assertEqual(movimiento.lote, self.lote)
        self.assertEqual(movimiento.documento, "FACT001")
        self.assertEqual(movimiento.notas, "Compra de inventario")
        self.assertIsNotNone(movimiento.fecha)
        self.assertTrue(isinstance(movimiento, MovimientoInventario))

    def test_movimiento_str(self):
        """Verifica el método __str__ de MovimientoInventario."""
        movimiento = MovimientoInventario.objects.create(
            tipo='entrada',
            origen='compra',
            producto=self.producto,
            cantidad=Decimal('5.00'),
            stock_anterior=Decimal('10.00'),
            stock_nuevo=Decimal('15.00'),
            costo_unitario=Decimal('400.00'),
            almacen=self.almacen
        )
        self.assertEqual(str(movimiento), f"Entrada - {self.producto} - 5.00")

    def test_movimiento_cantidad_no_negativa(self):
        """Verifica que la cantidad no sea negativa."""
        with self.assertRaisesMessage(ValidationError, 'La cantidad no puede ser negativa.'):
            movimiento = MovimientoInventario(
                tipo='entrada',
                origen='compra',
                producto=self.producto,
                cantidad=Decimal('-5.00'),
                stock_anterior=Decimal('10.00'),
                stock_nuevo=Decimal('5.00'),
                costo_unitario=Decimal('400.00'),
                almacen=self.almacen
            )
            movimiento.full_clean()

    def test_movimiento_stock_consistente(self):
        """Verifica que el stock_nuevo sea consistente con el tipo de movimiento."""
        with self.assertRaisesMessage(ValidationError, 'El stock nuevo no coincide con el cálculo esperado.'):
            movimiento = MovimientoInventario(
                tipo='entrada',
                origen='compra',
                producto=self.producto,
                cantidad=Decimal('5.00'),
                stock_anterior=Decimal('10.00'),
                stock_nuevo=Decimal('14.00'),  # Debería ser 15
                costo_unitario=Decimal('400.00'),
                almacen=self.almacen
            )
            movimiento.full_clean()

    def test_movimiento_costo_unitario_entrada(self):
        """Verifica que el costo unitario sea obligatorio para entradas."""
        with self.assertRaisesMessage(ValidationError, 'El costo unitario es obligatorio para movimientos de entrada.'):
            movimiento = MovimientoInventario(
                tipo='entrada',
                origen='compra',
                producto=self.producto,
                cantidad=Decimal('5.00'),
                stock_anterior=Decimal('10.00'),
                stock_nuevo=Decimal('15.00'),
                almacen=self.almacen
            )
            movimiento.full_clean()

    def test_movimiento_stock_suficiente_salida(self):
        """Verifica que la cantidad no exceda el stock disponible para salidas."""
        with self.assertRaisesMessage(ValidationError, 'La cantidad solicitada excede el stock disponible en el almacén.'):
            movimiento = MovimientoInventario(
                tipo='salida',
                origen='venta',
                producto=self.producto,
                cantidad=Decimal('15.00'),  # Stock en almacén es 10
                stock_anterior=Decimal('10.00'),
                stock_nuevo=Decimal('0.00'),
                almacen=self.almacen
            )
            movimiento.full_clean()

    def test_movimiento_lote_valido(self):
        """Verifica que el lote corresponda al producto."""
        producto2 = Producto.objects.create(
            codigo="TV002",
            nombre="Smart TV 65\"",
            categoria=self.categoria,
            precio_venta=Decimal('800.00')
        )
        lote_invalido = Lote.objects.create(
            producto=producto2,
            numero_lote="LOTE2023-002",
            cantidad=Decimal('10.00'),
            almacen=self.almacen
        )
        with self.assertRaisesMessage(ValidationError, 'El lote debe corresponder al producto seleccionado.'):
            movimiento = MovimientoInventario(
                tipo='entrada',
                origen='compra',
                producto=self.producto,
                cantidad=Decimal('5.00'),
                stock_anterior=Decimal('10.00'),
                stock_nuevo=Decimal('15.00'),
                costo_unitario=Decimal('400.00'),
                almacen=self.almacen,
                lote=lote_invalido
            )
            movimiento.full_clean()

    # Nuevos tests
    def test_movimiento_actualiza_stock(self):
        """Verifica que el movimiento actualice StockAlmacen y Producto.stock."""
        movimiento = MovimientoInventario.objects.create(
            tipo='entrada',
            origen='compra',
            producto=self.producto,
            cantidad=Decimal('5.00'),
            stock_anterior=Decimal('10.00'),
            stock_nuevo=Decimal('15.00'),
            costo_unitario=Decimal('400.00'),
            almacen=self.almacen
        )
        self.stock_almacen.refresh_from_db()
        self.producto.refresh_from_db()
        self.assertEqual(self.stock_almacen.cantidad, Decimal('15.00'))
        self.assertEqual(self.producto.stock, Decimal('15.00'))

    def test_movimiento_todos_tipos(self):
        """Verifica todos los tipos de movimiento."""
        tipos = ['entrada', 'salida', 'ajuste', 'devolucion', 'traslado']
        for tipo in tipos:
            stock_nuevo = Decimal('15.00') if tipo == 'entrada' else Decimal('5.00')
            movimiento = MovimientoInventario.objects.create(
                tipo=tipo,
                origen='compra' if tipo == 'entrada' else 'venta',
                producto=self.producto,
                cantidad=Decimal('5.00'),
                stock_anterior=Decimal('10.00'),
                stock_nuevo=stock_nuevo,
                costo_unitario=Decimal('400.00') if tipo == 'entrada' else None,
                almacen=self.almacen
            )
            self.assertEqual(movimiento.tipo, tipo)

    def test_movimiento_campos_opcionales(self):
        """Verifica que los campos opcionales puedan ser nulos o vacíos."""
        movimiento = MovimientoInventario.objects.create(
            tipo='salida',
            origen='venta',
            producto=self.producto,
            cantidad=Decimal('5.00'),
            stock_anterior=Decimal('10.00'),
            stock_nuevo=Decimal('5.00'),
            almacen=self.almacen,
            proveedor=None,
            lote=None,
            documento="",
            notas="",
            referencia_id=None,
            referencia_tipo=""
        )
        self.assertIsNone(movimiento.proveedor)
        self.assertIsNone(movimiento.lote)
        self.assertEqual(movimiento.documento, "")
        self.assertEqual(movimiento.notas, "")
        self.assertIsNone(movimiento.referencia_id)
        self.assertEqual(movimiento.referencia_tipo, "")

    def test_movimiento_documento_max_length(self):
        """Verifica la longitud máxima del campo documento."""
        with self.assertRaises(ValidationError):
            movimiento = MovimientoInventario(
                tipo='entrada',
                origen='compra',
                producto=self.producto,
                cantidad=Decimal('5.00'),
                stock_anterior=Decimal('10.00'),
                stock_nuevo=Decimal('15.00'),
                costo_unitario=Decimal('400.00'),
                almacen=self.almacen,
                documento="A" * 51
            )
            movimiento.full_clean()