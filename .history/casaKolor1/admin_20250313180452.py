from django.contrib import admin
from .models import productos,CarritoItem


#cambio

class productosAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'imagen', 'descripcion', 'precio', 'fecha_creacion', 'categoria')
    list_filter = ('categoria',)  # Filtro por categoría en el panel de administración
    search_fields = ('nombre', 'categoria')  # Permitir búsqueda por nombre y categoría

admin.site.register(productos, productosAdmin)

class CarritoItemAdmin(admin.ModelAdmin):
    list_display = ('producto', 'cantidad', 'usuario', 'sesion_id', 'fecha_creacion')
    list_filter = ('fecha_creacion',)
    search_fields = ('producto__nombre', 'usuario__username')

admin.site.register(CarritoItem, CarritoItemAdmin)

class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    readonly_fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal')

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