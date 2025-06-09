from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.utils import IntegrityError
from datetime import date, timedelta
from decimal import Decimal

from inventario.models.categoria import Categoria
from inventario.models.producto import Producto
from inventario.models.proveedor import Proveedor
from inventario.models.almacen import Almacen
from inventario.models.stock_almacen import StockAlmacen
from inventario.models.variacion import Variacion
from inventario.models.lote import Lote
from inventario.models.orden_compra import OrdenCompra, ItemOrdenCompra
from inventario.models.contacto_proveedor import ContactoProveedor
from inventario.models.movimiento import MovimientoInventario


class BaseModelTest(TestCase):
    def assert_max_length(self, model_class, field_name, max_length, valid_value, invalid_value, base_data):
        """Verifica la longitud máxima de un campo."""
        data = base_data.copy()
        data[field_name] = valid_value
        instance = model_class(**data)
        instance.full_clean()
        
        data[field_name] = invalid_value
        with self.assertRaisesMessage(ValidationError, f'Asegúrese de que este valor tenga menos de {max_length} caracteres'):
            instance = model_class(**data)
            instance.full_clean()

    def assert_optional_fields(self, model_class, optional_fields, required_fields, setup_data):
        """Verifica que los campos opcionales puedan estar vacíos y los requeridos no."""
        data = setup_data.copy()
        for field in optional_fields:
            data[field] = "" if isinstance(data.get(field), str) else None
        instance = model_class(**data)
        instance.full_clean()

        for field in required_fields:
            data = setup_data.copy()
            data[field] = "" if isinstance(data.get(field), str) else None
            with self.assertRaises(ValidationError):
                instance = model_class(**data)
                instance.full_clean()


class CategoriaModelTest(BaseModelTest):
    def test_categoria_creacion(self):
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
        categoria = Categoria.objects.create(nombre="Electrónica")
        self.assertEqual(str(categoria), "Electrónica")

    def test_categoria_codigo_unico(self):
        Categoria.objects.create(nombre="Electrónica", codigo="ELEC")
        with self.assertRaises(IntegrityError):
            Categoria.objects.create(nombre="Gadgets", codigo="ELEC")

    def test_categoria_relacion_padre(self):
        parent_categoria = Categoria.objects.create(nombre="Electrónica")
        child_categoria = Categoria.objects.create(
            nombre="Televisores",
            categoria_padre=parent_categoria
        )
        self.assertEqual(child_categoria.categoria_padre, parent_categoria)
        self.assertIn(child_categoria, parent_categoria.subcategorias.all())

    def test_categoria_ruta_completa(self):
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
        categoria1 = Categoria.objects.create(nombre="Zapatillas", orden=1)
        categoria2 = Categoria.objects.create(nombre="Camisetas", orden=1)
        categoria3 = Categoria.objects.create(nombre="Accesorios", orden=2)
        categorias = Categoria.objects.all()
        self.assertEqual(categorias[0].nombre, "Camisetas")
        self.assertEqual(categorias[1].nombre, "Zapatillas")
        self.assertEqual(categorias[2].nombre, "Accesorios")

    def test_categoria_no_ciclo(self):
        categoria = Categoria.objects.create(nombre="Electrónica")
        categoria.categoria_padre = categoria
        with self.assertRaisesMessage(ValidationError, 'Una categoría no puede ser su propio padre.'):
            categoria.full_clean()

    def test_categoria_ciclo_indirecto(self):
        cat_a = Categoria.objects.create(nombre="A")
        cat_b = Categoria.objects.create(nombre="B", categoria_padre=cat_a)
        cat_c = Categoria.objects.create(nombre="C", categoria_padre=cat_b)
        cat_a.categoria_padre = cat_c
        with self.assertRaisesMessage(ValidationError, 'Una categoría no puede ser su propio padre.'):
            cat_a.full_clean()

    def test_categoria_orden_no_negativo(self):
        with self.assertRaisesMessage(ValidationError, 'El orden no puede ser negativo.'):
            categoria = Categoria(nombre="Electrónica", orden=-1)
            categoria.full_clean()

    def test_categoria_imagen_nullable(self):
        categoria = Categoria.objects.create(nombre="Electrónica", imagen=None)
        self.assertFalse(categoria.imagen)

    def test_categoria_nombre_max_length(self):
        self.assert_max_length(
            model_class=Categoria,
            field_name="nombre",
            max_length=100,
            valid_value="A" * 100,
            invalid_value="A" * 101,
            base_data={"nombre": "Test", "codigo": None}
        )

    def test_categoria_codigo_max_length(self):
        self.assert_max_length(
            model_class=Categoria,
            field_name="codigo",
            max_length=20,
            valid_value="A" * 20,
            invalid_value="A" * 21,
            base_data={"nombre": "Test", "codigo": None}
        )

    def test_categoria_campos_opcionales(self):
        self.assert_optional_fields(
            model_class=Categoria,
            optional_fields=["descripcion", "imagen", "codigo", "categoria_padre"],
            required_fields=["nombre"],
            setup_data={"nombre": "Electrónica", "descripcion": "Test", "codigo": "ELEC"}
        )


class ProveedorModelTest(BaseModelTest):
    def test_proveedor_creacion(self):
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
        proveedor = Proveedor.objects.create(nombre="Tech Supplier", ruc="1234567890001")
        self.assertEqual(str(proveedor), "Tech Supplier")

    def test_proveedor_ruc_unico(self):
        Proveedor.objects.create(nombre="Tech Supplier", ruc="1234567890001")
        with self.assertRaises(IntegrityError):
            Proveedor.objects.create(nombre="Other Supplier", ruc="1234567890001")

    def test_proveedor_limite_credito_no_negativo(self):
        with self.assertRaisesMessage(ValidationError, 'El límite de crédito no puede ser negativo.'):
            proveedor = Proveedor(
                nombre="Tech Supplier",
                ruc="9876543210001",
                limite_credito=Decimal('-1000.00')
            )
            proveedor.full_clean()

    def test_proveedor_optional_fields(self):
        self.assert_optional_fields(
            model_class=Proveedor,
            optional_fields=["direccion", "telefono", "email", "sitio_web", "notas"],
            required_fields=["nombre", "ruc"],
            setup_data={
                "nombre": "Tech Supplier",
                "ruc": "1234567890001",
                "direccion": "Test",
                "telefono": "123",
                "email": "test@test.com",
                "sitio_web": "http://test.com",
                "notas": "Test"
            }
        )

    def test_proveedor_ruc_max_length(self):
        self.assert_max_length(
            model_class=Proveedor,
            field_name="ruc",
            max_length=13,
            valid_value="A" * 13,
            invalid_value="A" * 14,
            base_data={"nombre": "Test", "ruc": "1234567890001"}
        )

    def test_proveedor_estado_choices(self):
        proveedor_activo = Proveedor.objects.create(nombre="Supplier1", ruc="1234567890001", estado='activo')
        proveedor_inactivo = Proveedor.objects.create(nombre="Supplier2", ruc="9876543210001", estado='inactivo')
        self.assertEqual(proveedor_activo.estado, 'activo')
        self.assertEqual(proveedor_inactivo.estado, 'inactivo')


class ContactoProveedorModelTest(BaseModelTest):
    def setUp(self):
        self.proveedor = Proveedor.objects.create(
            nombre="Tech Supplier",
            ruc="1234567890001"
        )

    def test_contacto_creacion(self):
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
        contacto = ContactoProveedor.objects.create(
            proveedor=self.proveedor,
            nombre="Ana Lopez"
        )
        self.assertEqual(str(contacto), f"Ana Lopez ({self.proveedor})")

    def test_contacto_relacion(self):
        contacto = ContactoProveedor.objects.create(
            proveedor=self.proveedor,
            nombre="Ana Lopez"
        )
        self.assertEqual(contacto.proveedor, self.proveedor)
        self.assertIn(contacto, self.proveedor.contactos.all())

    def test_contacto_optional_fields(self):
        self.assert_optional_fields(
            model_class=ContactoProveedor,
            optional_fields=["telefono", "email", "cargo"],
            required_fields=["proveedor", "nombre"],
            setup_data={
                "proveedor": self.proveedor,
                "nombre": "Ana Lopez",
                "telefono": "123",
                "email": "test@test.com",
                "cargo": "Test"
            }
        )

    def test_contacto_cascade_deletion(self):
        contacto = ContactoProveedor.objects.create(
            proveedor=self.proveedor,
            nombre="Ana Lopez"
        )
        self.proveedor.delete()
        self.assertFalse(ContactoProveedor.objects.filter(id=contacto.id).exists())

    def test_contacto_nombre_max_length(self):
        self.assert_max_length(
            model_class=ContactoProveedor,
            field_name="nombre",
            max_length=100,
            valid_value="A" * 100,
            invalid_value="A" * 101,
            base_data={"proveedor": self.proveedor, "nombre": "Test"}
        )


class AlmacenModelTest(BaseModelTest):
    def test_almacen_creacion(self):
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
        almacen = Almacen.objects.create(nombre="Bodega Principal")
        self.assertEqual(str(almacen), "Bodega Principal (Sin sucursal)")

    def test_almacen_optional_fields(self):
        self.assert_optional_fields(
            model_class=Almacen,
            optional_fields=["direccion", "responsable"],
            required_fields=["nombre"],
            setup_data={
                "nombre": "Bodega Principal",
                "direccion": "Test",
                "responsable": "Test"
            }
        )

    def test_almacen_activo_false(self):
        almacen = Almacen.objects.create(nombre="Bodega Inactiva", activo=False)
        self.assertFalse(almacen.activo)

    def test_almacen_nombre_max_length(self):
        self.assert_max_length(
            model_class=Almacen,
            field_name="nombre",
            max_length=100,
            valid_value="A" * 100,
            invalid_value="A" * 101,
            base_data={"nombre": "Test"}
        )


class StockAlmacenModelTest(BaseModelTest):
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
        stock = StockAlmacen.objects.create(
            producto=self.producto,
            almacen=self.almacen,
            cantidad=Decimal('10.00')
        )
        self.assertEqual(str(stock), f"{self.producto} - {self.almacen} - 10.00")

    def test_stock_almacen_unico(self):
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
        with self.assertRaisesMessage(ValidationError, 'La cantidad no puede ser negativa.'):
            stock = StockAlmacen(
                producto=self.producto,
                almacen=self.almacen,
                cantidad=Decimal('-5.00')
            )
            stock.full_clean()

    def test_stock_almacen_cascade_deletion(self):
        stock = StockAlmacen.objects.create(
            producto=self.producto,
            almacen=self.almacen,
            cantidad=Decimal('10.00')
        )
        self.producto.delete()
        self.assertFalse(StockAlmacen.objects.filter(id=stock.id).exists())
        
        self.producto = Producto.objects.create(
            codigo="TV002",
            nombre="Smart TV 65\"",
            categoria=self.categoria,
            precio_venta=Decimal('800.00'),
            stock=Decimal('0.00')
        )
        stock = StockAlmacen.objects.create(
            producto=self.producto,
            almacen=self.almacen,
            cantidad=Decimal('10.00')
        )
        self.almacen.delete()
        self.assertFalse(StockAlmacen.objects.filter(id=stock.id).exists())

    def test_stock_almacen_cantidad_precision(self):
        stock = StockAlmacen.objects.create(
            producto=self.producto,
            almacen=self.almacen,
            cantidad=Decimal('99999999.99')
        )
        self.assertEqual(stock.cantidad, Decimal('99999999.99'))
        with self.assertRaises(ValidationError):
            stock.cantidad = Decimal('100000000.00')
            stock.full_clean()


class VariacionModelTest(BaseModelTest):
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
        variacion = Variacion.objects.create(
            producto=self.producto,
            atributo="Color: Azul, Talla: M",
            codigo="CAM001-AZUL-M",
            precio_venta=Decimal('22.00')
        )
        self.assertEqual(str(variacion), f"{self.producto} - Color: Azul, Talla: M")

    def test_variacion_codigo_unico(self):
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
        self.assertEqual(self.producto.stock, Decimal('8.00'))

    def test_variacion_imagen_nullable(self):
        variacion = Variacion.objects.create(
            producto=self.producto,
            atributo="Color: Azul, Talla: M",
            codigo="CAM001-AZUL-M",
            precio_venta=Decimal('22.00'),
            imagen=None
        )
        self.assertFalse(variacion.imagen)

    def test_variacion_atributo_max_length(self):
        self.assert_max_length(
            model_class=Variacion,
            field_name="atributo",
            max_length=100,
            valid_value="A" * 100,
            invalid_value="A" * 101,
            base_data={
                "producto": self.producto,
                "atributo": "Test",
                "codigo": "TEST001",
                "precio_venta": Decimal('20.00')
            }
        )

    def test_variacion_cascade_deletion(self):
        variacion = Variacion.objects.create(
            producto=self.producto,
            atributo="Color: Azul, Talla: M",
            codigo="CAM001-AZUL-M",
            precio_venta=Decimal('22.00')
        )
        self.producto.delete()
        self.assertFalse(Variacion.objects.filter(id=variacion.id).exists())


class LoteModelTest(BaseModelTest):
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
        lote = Lote.objects.create(
            producto=self.producto,
            numero_lote="LOTE2023-001",
            cantidad=Decimal('100.00'),
            almacen=self.almacen
        )
        self.assertEqual(str(lote), f"{self.producto} - Lote LOTE2023-001")

    def test_lote_cantidad_no_negativa(self):
        with self.assertRaisesMessage(ValidationError, 'La cantidad no puede ser negativa.'):
            lote = Lote(
                producto=self.producto,
                numero_lote="LOTE2023-001",
                cantidad=Decimal('-100.00'),
                almacen=self.almacen
            )
            lote.full_clean()

    def test_lote_fechas_validas(self):
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

    def test_lote_fechas_nullable(self):
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
        self.assert_max_length(
            model_class=Lote,
            field_name="numero_lote",
            max_length=50,
            valid_value="A" * 50,
            invalid_value="A" * 51,
            base_data={
                "producto": self.producto,
                "numero_lote": "TEST",
                "cantidad": Decimal('100.00'),
                "almacen": self.almacen
            }
        )

    def test_lote_protect_deletion(self):
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

    def test_lote_actualiza_stock_almacen(self):
        lote = Lote.objects.create(
            producto=self.producto,
            numero_lote="LOTE2023-001",
            cantidad=Decimal('100.00'),
            almacen=self.almacen
        )
        stock_almacen = StockAlmacen.objects.get(producto=self.producto, almacen=self.almacen)
        self.assertEqual(stock_almacen.cantidad, Decimal('100.00'))
        
        lote.cantidad = Decimal('150.00')
        lote.save()
        stock_almacen.refresh_from_db()
        self.assertEqual(stock_almacen.cantidad, Decimal('150.00'))


class OrdenCompraModelTest(BaseModelTest):
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
            precio_venta=Decimal('600.00'),
            stock=Decimal('0.00')
        )
        self.almacen = Almacen.objects.create(nombre="Bodega Principal", activo=True)

    def test_orden_compra_creacion(self):
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
        orden = OrdenCompra.objects.create(
            proveedor=self.proveedor,
            numero="OC001",
            fecha=date.today()
        )
        self.assertEqual(str(orden), f"Orden OC001 - {self.proveedor}")

    def test_orden_compra_numero_unico(self):
        orden = OrdenCompra.objects.create(
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
        with self.assertRaisesMessage(ValidationError, 'El total no puede ser negativo.'):
            orden = OrdenCompra(
                proveedor=self.proveedor,
                numero="OC001",
                fecha=date.today(),
                total=Decimal('-100.00')
            )
            orden.full_clean()

    def test_item_orden_compra_creacion(self):
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
        self.assertEqual(item.subtotal, Decimal('2500.00'))
        self.assertTrue(isinstance(item, ItemOrdenCompra))

    def test_item_orden_compra_str(self):
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
        self.assertEqual(item.subtotal, Decimal('5000.00'))
        orden.refresh_from_db()
        self.assertEqual(orden.total, Decimal('5000.00'))

    def test_item_orden_compra_valores_no_negativos(self):
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

    def test_orden_compra_estado_transiciones(self):
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
        orden = OrdenCompra.objects.create(
            proveedor=self.proveedor,
            numero="OC001",
            fecha=date.today()
        )
        with self.assertRaises(IntegrityError):
            self.proveedor.delete()

    def test_orden_compra_completada_genera_movimiento(self):
        orden = OrdenCompra.objects.create(
            proveedor=self.proveedor,
            numero="OC001",
            fecha=date.today(),
            estado='pendiente'
        )
        ItemOrdenCompra.objects.create(
            orden_compra=orden,
            producto=self.producto,
            cantidad=Decimal('5.00'),
            precio_unitario=Decimal('500.00')
        )
        StockAlmacen.objects.create(producto=self.producto, almacen=self.almacen, cantidad=Decimal('0.00'))
        
        orden.estado = 'completada'
        orden.save()
        movimiento = MovimientoInventario.objects.get(
            producto=self.producto,
            origen='compra',
            almacen=self.almacen,
            referencia_id=orden.id,
            referencia_tipo='orden_compra'
        )
        self.assertEqual(movimiento.tipo, 'entrada')
        self.assertEqual(movimiento.cantidad, Decimal('5.00'))
        self.assertEqual(movimiento.costo_unitario, Decimal('500.00'))


class ProductoModelTest(BaseModelTest):
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
            stock=Decimal('0.00')
        )

    def test_producto_creacion(self):
        producto = Producto.objects.create(
            codigo="TV002",
            nombre="Smart TV 65\"",
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
        self.assertEqual(producto.codigo, "TV002")
        self.assertEqual(producto.nombre, "Smart TV 65\"")
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
        self.assertEqual(producto.url_slug, "smart-tv-65")
        self.assertIn(self.proveedor, producto.proveedores.all())
        self.assertTrue(isinstance(producto, Producto))

    def test_producto_str(self):
        self.assertEqual(str(self.producto), "TV001 - Smart TV 55\"")

    def test_producto_codigo_unico(self):
        with self.assertRaises(IntegrityError):
            Producto.objects.create(
                codigo="TV001",
                nombre="Smart TV 65\"",
                categoria=self.categoria,
                precio_venta=Decimal('800.00'),
                stock=Decimal('0.00')
            )

    def test_producto_disponible(self):
        producto_activo = Producto.objects.create(
            codigo="TV002",
            nombre="Smart TV 65\"",
            categoria=self.categoria,
            precio_venta=Decimal('600.00'),
            stock=Decimal('5.00'),
            estado='activo',
            es_inventariable=True
        )
        self.assertTrue(producto_activo.disponible)

        producto_inactivo = Producto.objects.create(
            codigo="TV003",
            nombre="Smart TV 75\"",
            categoria=self.categoria,
            precio_venta=Decimal('800.00'),
            stock=Decimal('5.00'),
            estado='inactivo',
            es_inventariable=True
        )
        self.assertFalse(producto_inactivo.disponible)

        producto_sin_stock = Producto.objects.create(
            codigo="TV004",
            nombre="Smart TV 85\"",
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
        producto = Producto.objects.create(
            codigo="TV002",
            nombre="Smart TV 65\"",
            categoria=self.categoria,
            precio_compra=Decimal('400.00'),
            precio_venta=Decimal('600.00'),
            stock=Decimal('0.00')
        )
        self.assertEqual(producto.margen, Decimal('50.0'))

        producto_sin_compra = Producto.objects.create(
            codigo="TV003",
            nombre="Smart TV 75\"",
            categoria=self.categoria,
            precio_compra=Decimal('0.00'),
            precio_venta=Decimal('800.00'),
            stock=Decimal('0.00')
        )
        self.assertEqual(producto_sin_compra.margen, Decimal('0.0'))

    def test_producto_url_slug(self):
        producto = Producto.objects.create(
            codigo="TV002",
            nombre="Smart TV 65\"",
            categoria=self.categoria,
            precio_venta=Decimal('600.00'),
            stock=Decimal('0.00')
        )
        self.assertEqual(producto.url_slug, "smart-tv-65")

    def test_producto_valores_no_negativos(self):
        for field, error_msg in [
            ('precio_compra', 'El precio de compra no puede ser negativo.'),
            ('precio_venta', 'El precio de venta no puede ser negativo.'),
            ('iva', 'El IVA no puede ser negativo.'),
            ('stock', 'El stock no puede ser negativo.'),
            ('stock_minimo', 'El stock mínimo no puede ser negativo.')
        ]:
            data = {
                "codigo": f"TEST{field}",
                "nombre": "Test",
                "categoria": self.categoria,
                "precio_venta": Decimal('600.00'),
                "stock": Decimal('0.00'),
                field: Decimal('-1.00')
            }
            with self.assertRaisesMessage(ValidationError, error_msg):
                producto = Producto(**data)
                producto.full_clean()

    def test_producto_imagen_nullable(self):
        producto = Producto.objects.create(
            codigo="TV002",
            nombre="Smart TV 65\"",
            categoria=self.categoria,
            precio_venta=Decimal('600.00'),
            stock=Decimal('0.00'),
            imagen=None
        )
        self.assertFalse(producto.imagen)

    def test_producto_proveedores_multiple(self):
        proveedor2 = Proveedor.objects.create(nombre="Supplier2", ruc="9876543210001")
        producto = Producto.objects.create(
            codigo="TV002",
            nombre="Smart TV 65\"",
            categoria=self.categoria,
            precio_venta=Decimal('600.00'),
            stock=Decimal('0.00')
        )
        producto.proveedores.add(self.proveedor, proveedor2)
        self.assertEqual(producto.proveedores.count(), 2)
        producto.proveedores.remove(self.proveedor)
        self.assertEqual(producto.proveedores.count(), 1)

    def test_producto_estado_y_tipo_choices(self):
        producto_activo = Producto.objects.create(
            codigo="TV002",
            nombre="Smart TV 65\"",
            categoria=self.categoria,
            precio_venta=Decimal('600.00'),
            stock=Decimal('0.00'),
            estado='activo',
            tipo='producto'
        )
        producto_inactivo = Producto.objects.create(
            codigo="TV003",
            nombre="Smart TV 75\"",
            categoria=self.categoria,
            precio_venta=Decimal('800.00'),
            stock=Decimal('0.00'),
            estado='inactivo',
            tipo='servicio'
        )
        self.assertEqual(producto_activo.estado, 'activo')
        self.assertEqual(producto_activo.tipo, 'producto')
        self.assertEqual(producto_inactivo.estado, 'inactivo')
        self.assertEqual(producto_inactivo.tipo, 'servicio')

    def test_producto_codigo_max_length(self):
        self.assert_max_length(
            model_class=Producto,
            field_name="codigo",
            max_length=50,
            valid_value="A" * 50,
            invalid_value="A" * 51,
            base_data={
                "codigo": "TEST",
                "nombre": "Test",
                "categoria": self.categoria,
                "precio_venta": Decimal('600.00'),
                "stock": Decimal('0.00')
            }
        )

    def test_producto_stock_actualiza_con_stock_almacen(self):
        almacen = Almacen.objects.create(nombre="Bodega Principal")
        self.producto.stock = Decimal('0.00')
        self.producto.save()
        stock_almacen = StockAlmacen.objects.create(producto=self.producto, almacen=almacen, cantidad=Decimal('10.00'))
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, Decimal('10.00'))
        
        stock_almacen.cantidad = Decimal('15.00')
        stock_almacen.save()
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, Decimal('15.00'))
        
        stock_almacen.delete()
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, Decimal('0.00'))

    def test_producto_stock_actualiza_con_variacion_eliminada(self):
        self.producto.stock = Decimal('0.00')
        self.producto.save()
        variacion = Variacion.objects.create(
            producto=self.producto,
            atributo="Color: Azul",
            codigo="TV001-AZUL",
            stock=Decimal('5.00'),
            precio_venta=Decimal('600.00')
        )
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, Decimal('5.00'))
        
        variacion.delete()
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, Decimal('0.00'))


class MovimientoInventarioModelTest(BaseModelTest):
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
        with self.assertRaisesMessage(ValidationError, 'El stock nuevo no coincide con el cálculo esperado.'):
            movimiento = MovimientoInventario(
                tipo='entrada',
                origen='compra',
                producto=self.producto,
                cantidad=Decimal('5.00'),
                stock_anterior=Decimal('10.00'),
                stock_nuevo=Decimal('14.00'),
                costo_unitario=Decimal('400.00'),
                almacen=self.almacen
            )
            movimiento.full_clean()

    def test_movimiento_costo_unitario_entrada(self):
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
        with self.assertRaisesMessage(ValidationError, 'La cantidad solicitada excede el stock disponible en el almacén.'):
            movimiento = MovimientoInventario(
                tipo='salida',
                origen='venta',
                producto=self.producto,
                cantidad=Decimal('15.00'),
                stock_anterior=Decimal('10.00'),
                stock_nuevo=Decimal('0.00'),
                almacen=self.almacen
            )
            movimiento.full_clean()

    def test_movimiento_lote_valido(self):
        producto2 = Producto.objects.create(
            codigo="TV002",
            nombre="Smart TV 65\"",
            categoria=self.categoria,
            precio_venta=Decimal('800.00'),
            stock=Decimal('0.00')
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

    def test_movimiento_updates_stock_and_almacen(self):
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
        tipos = [
            ('entrada', 'compra', Decimal('15.00'), Decimal('400.00')),
            ('salida', 'venta', Decimal('5.00'), None),
            ('ajuste', 'ajuste_manual', Decimal('10.00'), None),
            ('devolucion', 'devolucion_cliente', Decimal('10.00'), None),
            ('traslado', 'traslado', Decimal('10.00'), None)
        ]
        for i, (tipo, origen, expected_stock_nuevo, costo_unitario) in enumerate(tipos):
            # Actualizar StockAlmacen para reflejar stock_anterior
            self.stock_almacen.cantidad = Decimal('10.00')
            self.stock_almacen.save()
            
            movimiento = MovimientoInventario.objects.create(
                tipo=tipo,
                origen=origen,
                producto=self.producto,
                cantidad=Decimal('5.00'),
                stock_anterior=Decimal('10.00'),
                costo_unitario=costo_unitario,
                almacen=self.almacen
            )
            self.assertEqual(movimiento.tipo, tipo)
            # Calcular stock_nuevo esperado según la señal
            if tipo == 'entrada':
                self.assertEqual(movimiento.stock_nuevo, Decimal('15.00'))
            elif tipo == 'salida':
                self.assertEqual(movimiento.stock_nuevo, Decimal('5.00'))
            elif tipo == 'ajuste':
                self.assertEqual(movimiento.stock_nuevo, Decimal('5.00'))  # cantidad
            else:
                self.assertEqual(movimiento.stock_nuevo, Decimal('10.00'))  # stock_anterior
            # Actualizar stock para el siguiente movimiento
            self.stock_almacen.cantidad = movimiento.stock_nuevo
            self.stock_almacen.save()

    def test_movimiento_optional_fields(self):
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
        self.assert_max_length(
            model_class=MovimientoInventario,
            field_name="documento",
            max_length=50,
            valid_value="A" * 50,
            invalid_value="A" * 51,
            base_data={
                "tipo": "entrada",
                "origen": "compra",
                "producto": self.producto,
                "cantidad": Decimal('5.00'),
                "stock_anterior": Decimal('10.00'),
                "stock_nuevo": Decimal('15.00'),
                "costo_unitario": Decimal('400.00'),
                "almacen": self.almacen,
                "documento": "TEST"
            }
        )

    def test_movimiento_multi_almacen(self):
        almacen2 = Almacen.objects.create(nombre="Bodega Secundaria")
        StockAlmacen.objects.create(producto=self.producto, almacen=almacen2, cantidad=Decimal('5.00'))
        
        MovimientoInventario.objects.create(
            tipo='entrada',
            origen='compra',
            producto=self.producto,
            cantidad=Decimal('5.00'),
            stock_anterior=Decimal('10.00'),
            stock_nuevo=Decimal('15.00'),
            costo_unitario=Decimal('400.00'),
            almacen=self.almacen
        )
        MovimientoInventario.objects.create(
            tipo='entrada',
            origen='compra',
            producto=self.producto,
            cantidad=Decimal('3.00'),
            stock_anterior=Decimal('5.00'),
            stock_nuevo=Decimal('8.00'),
            costo_unitario=Decimal('400.00'),
            almacen=almacen2
        )
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, Decimal('23.00'))