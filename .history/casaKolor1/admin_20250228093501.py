from django.contrib import admin
from .models import productos, PrecioPresentacion, Sugerencia, Pedido, DetallePedido

class PrecioPresentacionInline(admin.TabularInline):
    model = PrecioPresentacion
    extra = 1

class productosAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'imagen', 'descripcion', 'precio', 'fecha_creacion', 'categoria')
    list_filter = ('categoria',)
    search_fields = ('nombre', 'categoria')
    
    def get_inlines(self, request, obj=None):
        # Solo mostrar opciones de presentación para pinturas
        if obj and obj.categoria == 'pinturas':
            return [PrecioPresentacionInline]
        return []

admin.site.register(productos, productosAdmin)

@admin.register(Sugerencia)
class SugerenciaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'correo', 'fecha_envio')
    search_fields = ('nombre', 'correo')

class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    readonly_fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal', 'presentacion')

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'correo', 'telefono', 'total', 'fecha_compra', 'estado')
    list_filter = ('estado', 'fecha_compra')
    search_fields = ('nombre', 'correo')
    readonly_fields = ('total',)
    inlines = [DetallePedidoInline]