from django.contrib import admin
from .models import productos  # Se mantiene el nombre en minúscula

class ProductosAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'imagen', 'descripcion', 'precio', 'presentacion', 'fecha_creacion', 'categoria')
    list_filter = ('categoria', 'presentacion')  # Agregamos filtro por presentación
    search_fields = ('nombre', 'categoria')  # Permitir búsqueda por nombre y categoría
    ordering = ('fecha_creacion',)  # Ordenar por fecha de creación

admin.site.register(productos, ProductosAdmin)



#sugerencias
from .models import Sugerencia


@admin.register(Sugerencia)
class SugerenciaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'correo', 'fecha_envio')
    search_fields = ('nombre', 'correo')


from .models import Pedido, DetallePedido

class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    readonly_fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal')

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'correo', 'telefono', 'total', 'fecha_compra', 'estado')
    list_filter = ('estado', 'fecha_compra')
    search_fields = ('nombre', 'correo')
    readonly_fields = ('total',)
    inlines = [DetallePedidoInline]