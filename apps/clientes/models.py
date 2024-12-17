from django.db import models

from apps.usuarios.models import Usuario


class Cliente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='cliente')
    identificacion = models.CharField(max_length=20)
    nombres = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=50)
    nacionalidad = models.CharField(max_length=30, blank=True, null=True)
    correo = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    genero = models.CharField(
        max_length=20,
        choices=[('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')],
        blank=True,
        null=True
    )
    fecha_registro = models.DateField(auto_now_add=True)
    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.identificacion}, {self.usuario.username}), {self.correo}, {self.telefono}, {self.genero}, {self.fecha_registro}, {self.nacionalidad}, {self.usuario.rol}"