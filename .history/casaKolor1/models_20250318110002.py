from django.db import models



class productos(models.Model):
   CATEGORIAS = [
       ('herramientas', 'Herramientas'),
       ('pinturas', 'Pinturas'),
   ]
   
   PRESENTACIONES = [
       ('cuarto', '1/4 de Galón'),
       ('galon', 'Galón'),
       ('dos_cinco', '2.5 Galones'),
       ('cinco', '5 Galones (Caneca)'),
   ]
   
   nombre = models.CharField(max_length=100)
   imagen = models.ImageField(upload_to='images/', null=True, blank=True)
   descripcion = models.TextField()
   precio = models.DecimalField(max_digits=10, decimal_places=0)
   presentacion = models.CharField(max_length=20, choices=PRESENTACIONES, default='galon')
   fecha_creacion = models.DateTimeField(auto_now_add=True)
   categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='herramientas')
   
   def __str__(self):
       return f"{self.nombre} - {self.get_presentacion_display()}"

#sugerencias


class Sugerencia(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField()
    sugerencia = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sugerencia de {self.nombre}"



from django.db import models
from django.contrib.auth.models import User
import uuid
import os

def comprobante_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('comprobantes', filename)

class Pedido(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField()
    telefono = models.CharField(max_length=20)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    comprobante = models.FileField(upload_to=comprobante_upload_path, null=True, blank=True)
    transaction_id = models.CharField(max_length=100, null=True)
    
    class Meta:
        ordering = ['-fecha_creacion']
        
    def __str__(self):
        return f"Pedido #{self.id} - {self.nombre}"
    

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey('productos', on_delete=models.SET_NULL, null=True)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"Detalle de {self.pedido} - {self.producto}"
    
    def save(self, *args, **kwargs):
        if not self.subtotal:
            self.subtotal = self.precio_unitario * self.cantidad
        super().save(*args, **kwargs)

