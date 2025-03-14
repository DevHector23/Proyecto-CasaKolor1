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

#sugerencias
from .models import Sugerencia


@admin.register(Sugerencia)
class SugerenciaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'correo', 'fecha_envio')
    search_fields = ('nombre', 'correo')

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(productos, on_delete=models.CASCADE, default=1)  # Cambia el valor predeterminado según tus necesidades
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=0)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'correo', 'telefono', 'total', 'fecha_compra', 'estado')
    list_filter = ('estado', 'fecha_compra')
    search_fields = ('nombre', 'correo')
    readonly_fields = ('total',)
    inlines = [DetallePedidoInline]