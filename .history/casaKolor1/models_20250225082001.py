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
        return f"Sugerencia de {self.nombre or 'a'}"



#factura
