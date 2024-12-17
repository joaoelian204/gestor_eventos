from django.db import models


class TipoEvento(models.Model):
    nombre = models.CharField(max_length=50, verbose_name="Nombre del Evento")
    descripcion = models.CharField(max_length=200, verbose_name="Descripción")
    categoria = models.CharField(max_length=50, verbose_name="Categoría")
    tipo_publico = models.CharField(max_length=50, verbose_name="Tipo de Público")

    class Meta:
        verbose_name = "Tipo de Evento"
        verbose_name_plural = "Tipos de Eventos"

    def __str__(self):
        return f"{self.nombre} - {self.categoria}"


class Evento(models.Model):
    tipo_evento = models.ForeignKey(TipoEvento, on_delete=models.CASCADE, verbose_name="Tipo de Evento")
    descripcion = models.CharField(max_length=200, verbose_name="Descripción del Evento")
    valor_referencial = models.FloatField(verbose_name="Valor Referencial")
    numero_horas_permitidas = models.IntegerField(verbose_name="Número de Horas Permitidas")
    valor_extra_hora = models.FloatField(verbose_name="Valor Extra por Hora")

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"

    def __str__(self):
        return f"{self.tipo_evento.nombre} - {self.descripcion}"

