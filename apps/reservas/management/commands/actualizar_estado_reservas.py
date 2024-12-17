# apps/reservas/management/commands/actualizar_reservas_auto.py

import time

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.reservas.models import Alquiler


class Command(BaseCommand):
    help = 'Actualiza el estado de las reservas automáticamente cada segundo'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Iniciando la actualización automática de reservas...'))
        
        try:
            while True:
                # Filtrar y actualizar las reservas en una sola consulta
                reservas_actualizadas = Alquiler.objects.filter(
                    estado='en_curso',
                    fecha_fin_reserva__lt=timezone.now()
                ).update(estado='finalizado')

                if reservas_actualizadas > 0:
                    self.stdout.write(self.style.SUCCESS(f'{reservas_actualizadas} reservas actualizadas a "finalizado".'))

                time.sleep(1)  # Esperar 1 segundo antes de la próxima ejecución
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Actualización automática detenida manualmente.'))
