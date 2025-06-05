from haystack import indexes
from .models import ProductoEcommerce, ServicioEcommerce, CategoriaEcommerce


class ProductoEcommerceIndex(indexes.SearchIndex, indexes.Indexable):
    """Índice de búsqueda para productos."""
    
    text = indexes.CharField(document=True, use_template=False)
    nombre = indexes.CharField(model_attr='producto__nombre')
    codigo = indexes.CharField(model_attr='producto__codigo', null=True)
    descripcion_corta = indexes.CharField(model_attr='descripcion_corta', null=True)
    descripcion_larga = indexes.CharField(model_attr='descripcion_larga', null=True)
    precio = indexes.FloatField(model_attr='producto__precio_venta')
    disponible = indexes.BooleanField()
    categorias = indexes.MultiValueField()
    destacado = indexes.BooleanField(model_attr='destacado')
    nuevo = indexes.BooleanField(model_attr='nuevo')
    oferta = indexes.BooleanField(model_attr='oferta')
    
    def get_model(self):
        return ProductoEcommerce
    
    def index_queryset(self, using=None):
        """Usado cuando el índice completo del modelo es actualizado."""
        return self.get_model().objects.filter(
            producto__mostrar_en_tienda=True,
            producto__estado='activo'
        )
    
    def prepare_disponible(self, obj):
        return obj.producto.stock > 0
    
    def prepare_categorias(self, obj):
        return [categoria.nombre for categoria in obj.categorias.all()]


class ServicioEcommerceIndex(indexes.SearchIndex, indexes.Indexable):
    """Índice de búsqueda para servicios."""
    
    text = indexes.CharField(document=True, use_template=False)
    nombre = indexes.CharField(model_attr='servicio__nombre')
    descripcion_corta = indexes.CharField(model_attr='descripcion_corta', null=True)
    descripcion_larga = indexes.CharField(model_attr='descripcion_larga', null=True)
    precio = indexes.FloatField(model_attr='servicio__precio')
    disponible = indexes.BooleanField(model_attr='servicio__disponible_online')
    tipo = indexes.CharField(model_attr='servicio__tipo')
    destacado = indexes.BooleanField(model_attr='destacado')
    
    def get_model(self):
        return ServicioEcommerce
    
    def index_queryset(self, using=None):
        """Usado cuando el índice completo del modelo es actualizado."""
        return self.get_model().objects.filter(servicio__disponible_online=True)


class CategoriaEcommerceIndex(indexes.SearchIndex, indexes.Indexable):
    """Índice de búsqueda para categorías."""
    
    text = indexes.CharField(document=True, use_template=False)
    nombre = indexes.CharField(model_attr='nombre')
    descripcion = indexes.CharField(model_attr='descripcion', null=True)
    activo = indexes.BooleanField(model_attr='activo')
    
    def get_model(self):
        return CategoriaEcommerce
    
    def index_queryset(self, using=None):
        """Usado cuando el índice completo del modelo es actualizado."""
        return self.get_model().objects.filter(activo=True)