from django.contrib import admin
from .models import productos


#cambio

class productosAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'imagen', 'descripcion', 'precio', 'fecha_creacion', 'categoria', 'colores_disponibles')
    list_filter = ('categoria',)
    search_fields = ('nombre', 'categoria')
    fieldsets = (
        (None, {
            'fields': ('nombre', 'imagen', 'descripcion', 'precio', 'categoria', 'presentacion')
        }),
        ('Opciones avanzadas', {
            'fields': ('colores_disponibles',),
            'classes': ('collapse',),
        }),
    )

admin.site.register(productos, productosAdmin)


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