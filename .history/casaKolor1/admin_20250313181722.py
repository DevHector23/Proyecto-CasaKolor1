from django.contrib import admin
from .models import productos, CarritoItem


#cambio
class productosAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'imagen', 'descripcion', 'precio', 'fecha_creacion', 'categoria')
    list_filter = ('categoria',)  # Filtro por categoría en el panel de administración
    search_fields = ('nombre', 'categoria')  # Permitir búsqueda por nombre y categoría

admin.site.register(productos, productosAdmin)


# Administración del Carrito
@admin.register(CarritoItem)
class CarritoItemAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'producto', 'cantidad', 'subtotal', 'fecha_agregado')
    list_filter = ('fecha_agregado',)
    search_fields = ('usuario__username', 'producto__nombre')
    
    def subtotal(self, obj):
        return obj.subtotal()
    subtotal.short_description = 'Subtotal'


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