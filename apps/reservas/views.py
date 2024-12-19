from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

from apps.clientes.models import Cliente
from apps.servicios.models import Combo, Servicio

from .models import Alquiler


# Verifica si el usuario es dueño
def es_dueño(user):
    ''' 
    Verifica si el usuario está autenticado y tiene el rol de 'dueño'.
    Retorna True si el usuario es dueño, de lo contrario, False.
    '''
    return user.is_authenticated and user.rol == 'dueño'


# Listar reservas activas
def listar_reservas(request):
    ''' 
    Muestra una lista de reservas activas asociadas al cliente actual.
    '''
    cliente = request.user.clientes
    reservas = Alquiler.objects.filter(cliente=cliente)
    return render(request, 'clientes/reservas_activas.html', {'reservas': reservas})


# Crear una reserva (alquiler) de un servicio o combo
def crear_alquiler(request):
    ''' 
    Crea una nueva reserva (alquiler) de un servicio o combo. 
    Valida los datos del formulario y envía un correo de confirmación al cliente.
    '''
    if request.method == 'POST':
        try:
            # Capturar y validar los datos del formulario
            cliente_id = request.POST.get('cliente_id')
            servicio_id = request.POST.get('servicio_id') or request.POST.get('evento_id')
            combo_id = request.POST.get('combo_id')
            direccion = request.POST.get('direccion')
            fecha_hora_reserva = request.POST.get('fecha_hora_reserva')
            fecha_fin_reserva = request.POST.get('fecha_fin_reserva', None)
            cantidad_unidades = int(request.POST.get('cantidad_unidades', 1))
            precio_por_unidad = request.POST.get('precio_por_unidad', '0').replace(',', '.')
            precio_por_unidad = float(precio_por_unidad)

            # Validaciones de campos obligatorios
            if not cliente_id or not direccion or not fecha_hora_reserva:
                return JsonResponse({'success': False, 'message': 'Todos los campos obligatorios deben ser completados.'})

            # Obtener el cliente
            cliente = get_object_or_404(Cliente, id=cliente_id)

            # Convertir fecha_hora_reserva a timezone-aware
            try:
                fecha_hora_reserva = datetime.strptime(fecha_hora_reserva, '%Y-%m-%dT%H:%M')
                fecha_hora_reserva = timezone.make_aware(fecha_hora_reserva)
            except ValueError:
                return JsonResponse({'success': False, 'message': 'La fecha de inicio tiene un formato incorrecto.'})

            if fecha_fin_reserva:
                try:
                    fecha_fin_reserva = datetime.strptime(fecha_fin_reserva, '%Y-%m-%dT%H:%M')
                    fecha_fin_reserva = timezone.make_aware(fecha_fin_reserva)
                except ValueError:
                    return JsonResponse({'success': False, 'message': 'La fecha de fin tiene un formato incorrecto.'})

            # Crear alquiler de servicio o combo según corresponda
            with transaction.atomic():
                if servicio_id:
                    servicio = get_object_or_404(Servicio, id=servicio_id)

                    # Verificar si ya existe una reserva activa para el servicio
                    if Alquiler.objects.filter(cliente=cliente, servicio=servicio, estado='en_curso', fecha_fin_reserva__gte=timezone.now()).exists():
                        return JsonResponse({'success': False, 'message': 'Ya tienes una reserva activa para este servicio.'})

                    # Calcular el costo total
                    costo_total = cantidad_unidades * precio_por_unidad

                    # Crear la nueva reserva de servicio
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

                elif combo_id:
                    combo = get_object_or_404(Combo, id=combo_id)

                    # Verificar si ya existe una reserva activa para el combo
                    if Alquiler.objects.filter(cliente=cliente, combo=combo, estado='en_curso', fecha_fin_reserva__gte=timezone.now()).exists():
                        return JsonResponse({'success': False, 'message': 'Ya tienes una reserva activa para este combo.'})

                    # Calcular el costo total para el combo
                    costo_total = float(combo.precio)

                    # Crear la nueva reserva de combo
                    Alquiler.objects.create(
                        cliente=cliente,
                        combo=combo,
                        direccion=direccion,
                        fecha_hora_reserva=fecha_hora_reserva,
                        fecha_fin_reserva=fecha_fin_reserva,
                        cantidad_unidades=1,
                        costo_total=costo_total,
                        estado='en_curso'
                    )

            # Enviar correo de confirmación al cliente
            if cliente.correo:
                html_content = render_to_string('emails/reserva_confirmada.html', {
                    'cliente': cliente,
                    'servicio': servicio if servicio_id else None,
                    'combo': combo if combo_id else None,
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

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error inesperado: {e}'})

    return JsonResponse({'success': False, 'message': 'Método no permitido.'})


# Ver detalle de una reserva
@user_passes_test(es_dueño)
def detalle_reserva(request, reserva_id):
    ''' 
    Muestra los detalles de una reserva específica.
    '''
    reserva = get_object_or_404(Alquiler, pk=reserva_id)
    return render(request, 'reservas/detalle_reserva.html', {'reserva': reserva})


# Editar una reserva
@user_passes_test(es_dueño)
def editar_reserva(request, reserva_id):
    ''' 
    Permite editar los detalles de una reserva específica.
    '''
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
    ''' 
    Permite eliminar una reserva específica.
    '''
    reserva = get_object_or_404(Alquiler, pk=reserva_id)
    reserva.delete()
    messages.success(request, 'Reserva eliminada correctamente.')
    return redirect('lista_reservas')
