from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

from apps.clientes.models import Cliente
from apps.eventos.models import Evento
from apps.servicios.models import Servicio

from .models import Alquiler


# Verifica si el usuario es dueño
def es_dueño(user):
    return user.is_authenticated and user.rol == 'dueño'

# Listar reservas activas

def listar_reservas(request):
    # Obtener las reservas del cliente actual (suponiendo que 'request.user' tiene acceso a 'cliente')
    cliente = request.user.cliente  # Asumiendo que tienes una relación OneToOne entre User y Cliente
    
    # Obtener todas las reservas relacionadas con el cliente actual
    reservas = Alquiler.objects.filter(cliente=cliente)
    
    return render(request, 'clientes/reservas_activas.html', {'reservas': reservas})

def crear_alquiler(request):
    if request.method == 'POST':
        try:
            # Capturar y validar los datos del formulario
            cliente_id = request.POST.get('cliente_id')
            servicio_id = request.POST.get('evento_id')
            direccion = request.POST.get('direccion')
            fecha_hora_reserva = request.POST.get('fecha_hora_reserva')
            fecha_fin_reserva = request.POST.get('fecha_fin_reserva', None)
            cantidad_unidades = int(request.POST.get('cantidad_unidades', 0))
            precio_por_unidad = request.POST.get('precio_por_unidad', '0').replace(',', '.')
            precio_por_unidad = float(precio_por_unidad)

            # Validaciones de campos
            if not cliente_id or not servicio_id or not direccion or not fecha_hora_reserva:
                return JsonResponse({'success': False, 'message': 'Todos los campos son obligatorios.'})

            costo_total = cantidad_unidades * precio_por_unidad

            # Obtener el cliente y el servicio
            cliente = get_object_or_404(Cliente, id=cliente_id)
            servicio = get_object_or_404(Servicio, id=servicio_id)

            # Bloquear si ya existe una reserva activa para el mismo servicio
            alquiler_existente = Alquiler.objects.filter(
                cliente=cliente,
                servicio=servicio,
                estado__in=['en_curso', 'pendiente'],
                fecha_fin_reserva__gte=timezone.now()
            ).exists()

            if alquiler_existente:
                return JsonResponse({'success': False, 'message': 'Ya tienes una reserva activa para este servicio.'})

            # Convertir fecha_hora_reserva a timezone-aware
            fecha_hora_reserva = datetime.strptime(fecha_hora_reserva, '%Y-%m-%dT%H:%M')
            fecha_hora_reserva = timezone.make_aware(fecha_hora_reserva)

            if fecha_fin_reserva:
                fecha_fin_reserva = datetime.strptime(fecha_fin_reserva, '%Y-%m-%dT%H:%M')
                fecha_fin_reserva = timezone.make_aware(fecha_fin_reserva)

            # Crear la nueva reserva con el estado 'en_curso'
            Alquiler.objects.create(
                cliente=cliente,
                servicio=servicio,
                direccion=direccion,
                fecha_hora_reserva=fecha_hora_reserva,
                fecha_fin_reserva=fecha_fin_reserva,
                cantidad_unidades=cantidad_unidades,
                costo_total=costo_total,
                estado='en_curso'
            )

            # Enviar correo de confirmación al cliente
            if cliente.correo:
                html_content = render_to_string('emails/reserva_confirmada.html', {
                    'cliente': cliente,
                    'servicio': servicio,
                    'direccion': direccion,
                    'fecha_hora_reserva': fecha_hora_reserva.strftime('%Y-%m-%d %H:%M'),
                    'fecha_fin_reserva': fecha_fin_reserva.strftime('%Y-%m-%d %H:%M') if fecha_fin_reserva else 'N/A',
                    'cantidad_unidades': cantidad_unidades,
                    'costo_total': f"{costo_total:.2f}"
                })

                text_content = strip_tags(html_content)
                subject = 'Reserva Confirmada'
                from_email = settings.EMAIL_HOST_USER
                to_email = [cliente.correo]

                email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
                email.attach_alternative(html_content, "text/html")

                try:
                    email.send(fail_silently=False)
                    return JsonResponse({'success': True, 'message': 'Reserva creada y correo enviado exitosamente.'})
                except Exception as e:
                    return JsonResponse({'success': False, 'message': f'Error al enviar el correo: {e}'})

            return JsonResponse({'success': True, 'message': 'Reserva creada exitosamente.'})

        except Cliente.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Cliente no encontrado.'})
        except Servicio.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Servicio no encontrado.'})
        except ValueError as e:
            return JsonResponse({'success': False, 'message': f'Error en los datos numéricos: {e}'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error inesperado: {e}'})

# Ver detalle de una reserva
@user_passes_test(es_dueño)
def detalle_reserva(request, reserva_id):
    reserva = get_object_or_404(Alquiler, pk=reserva_id)
    return render(request, 'reservas/detalle_reserva.html', {'reserva': reserva})

# Editar una reserva
@user_passes_test(es_dueño)
def editar_reserva(request, reserva_id):
    reserva = get_object_or_404(Alquiler, pk=reserva_id)
    if request.method == 'POST':
        reserva.fecha_alquiler = request.POST['fecha_alquiler']
        reserva.hora_inicio_reserva = request.POST['hora_inicio_reserva']
        reserva.hora_fin_planificada = request.POST['hora_fin_planificada']
        reserva.costo_alquiler = request.POST['costo_alquiler']
        reserva.save()
        messages.success(request, 'Reserva actualizada correctamente.')
        return redirect('lista_reservas')
    return render(request, 'reservas/editar_reserva.html', {'reserva': reserva})

# Eliminar una reserva
@user_passes_test(es_dueño)
def eliminar_reserva(request, reserva_id):
    reserva = get_object_or_404(Alquiler, pk=reserva_id)
    reserva.delete()
    messages.success(request, 'Reserva eliminada correctamente.')
    return redirect('lista_reservas')

def reservar_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    return render(request, 'eventos/reservar_evento.html', {'evento': evento})

def detalle_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    return render(request, 'eventos/detalle_evento.html', {'evento': evento})