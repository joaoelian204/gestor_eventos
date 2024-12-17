from cloudinary.models import CloudinaryField
from django.core.exceptions import ValidationError
from django.db import models


class Servicio(models.Model):
    TITULOS_OPCIONALES = [
        ('individual', 'Individual'),
        ('combo', 'Combo'),
    ]

    titulo = models.CharField(max_length=100, help_text="Título del servicio, ej. Alquiler de sillas")
    descripcion = models.TextField(help_text="Descripción del servicio ofrecido")
    valor_por_unidad = models.DecimalField(max_digits=10, decimal_places=2, help_text="Valor por unidad del servicio")
    tipo_servicio = models.CharField(
        max_length=20, choices=TITULOS_OPCIONALES, default='individual', help_text="Especifica si el servicio es individual o parte de un combo"
    )
    imagen_referencial = CloudinaryField('imagen', blank=True, null=True, help_text="Imagen referencial del servicio")

    def clean(self):
        """Valida que el valor del servicio sea mayor que 0"""
        if self.valor_por_unidad <= 0:
            raise ValidationError('El valor por unidad debe ser un número positivo.')

    def __str__(self):
        return self.titulo

    
class Combo(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    servicios_incluidos = models.ManyToManyField(Servicio, related_name='combos', blank=True)

    def clean(self):
        if self.precio <= 0:
            raise ValidationError('El precio del combo debe ser mayor que cero.')

    def __str__(self):
        return self.nombre


class ImagenCombo(models.Model):
    combo = models.ForeignKey(Combo, related_name='imagenes', on_delete=models.CASCADE)
    imagen = CloudinaryField('image')
    descripcion = models.CharField(max_length=255, blank=True, null=True)

    def clean(self):
        """Valida que la imagen no exceda un tamaño máximo"""
        if self.imagen and self.imagen.size > 5 * 1024 * 1024:  # Limitar el tamaño de la imagen a 5MB
            raise ValidationError("La imagen no debe exceder los 5MB.")

    def __str__(self):
        return f"Imagen de {self.combo.nombre}"

