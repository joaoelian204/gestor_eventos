from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now


class Usuario(AbstractUser):
    ROLES = (
        ('administrador', 'Administrador'),
        ('dueño', 'Dueño'),
        ('cliente', 'Cliente'),
    )
    rol = models.CharField(max_length=20, choices=ROLES, default='cliente')
    fecha_creacion = models.DateTimeField(default=now, editable=False)  # Campo para la fecha de creación
