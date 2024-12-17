from django.db import models
from django.utils import timezone

from apps.clientes.models import Cliente
from apps.servicios.models import Servicio


class Alquiler(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_curso', 'En Curso'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, default=1)
    direccion = models.CharField(max_length=255, default="Sin dirección")
    fecha_hora_reserva = models.DateTimeField(default=timezone.now)
    cantidad_unidades = models.PositiveIntegerField(default=1)
    costo_total = models.FloatField()  # Costo total calculado
    fecha_fin_reserva = models.DateTimeField(blank=True, null=True)
    hora_fin_planificada = models.TimeField(blank=True, null=True)
    hora_fin_real = models.TimeField(blank=True, null=True)
    calificacion_cliente = models.IntegerField(blank=True, null=True)
    calificacion_negocio = models.IntegerField(blank=True, null=True)
    observacion = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')

    def __str__(self):
        return f"Alquiler {self.id} - {self.servicio.titulo}"