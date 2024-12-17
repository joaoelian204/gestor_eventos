from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models


def validate_telefono(value):
    """
    Valida que el teléfono tenga exactamente 10 dígitos y no contenga letras.
    """
    if not value.isdigit() or len(value) != 10:
        raise ValidationError('El número de teléfono debe tener exactamente 10 dígitos.')

class Negocio(models.Model):
    nombre = models.CharField(max_length=100)
    logo = models.ImageField(
        upload_to='logos/',
        default='logos/default_logo.png',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'], message="Solo se permiten archivos JPG, JPEG y PNG.")]
    )
    direccion_principal = models.CharField(max_length=150)
    direccion_secundaria = models.CharField(max_length=150, blank=True, null=True)
    telefono = models.CharField(
        max_length=10,
        validators=[validate_telefono],
        help_text="El teléfono debe tener exactamente 10 dígitos."
    )
    correo = models.EmailField()
    pagina_web = models.URLField(blank=True, null=True)
    redes_sociales = models.JSONField(blank=True, null=True, default=dict)

    def __str__(self):
        return self.nombre


