from django.contrib import admin
from .models import productos


#cambio

class productosAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'imagen', 'descripcion', 'precio', 'fecha_creacion', 'categoria')
    list_filter = ('categoria',)  # Filtro por categoría en el panel de administración
    search_fields = ('nombre', 'categoria')  # Permitir búsqueda por nombre y categoría

admin.site.register(productos, productosAdmin)


#sugerencias
from .models import Sugerencia


@admin.register(Sugerencia)
class SugerenciaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'correo', 'fecha_envio')
    search_fields = ('nombre', 'correo')
