import tempfile
from datetime import datetime

from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.dateparse import parse_date
from weasyprint import HTML

from apps.administrador.models import Negocio
from apps.clientes.models import Cliente
from apps.reservas.models import Alquiler


# Verifica si el usuario es dueño
def es_dueño(user):
    ''' 
    Verifica si el usuario está autenticado y tiene el rol de 'dueño'.
    Retorna True si el usuario es dueño, de lo contrario, False.
    '''
    return user.is_authenticated and user.rol == 'dueño'


# Generar factura en PDF para una reserva de combo o servicio
def generar_factura_pdf(request, reserva_id):
    ''' 
    Genera una factura en formato PDF para una reserva específica de combo o servicio.
    La factura incluye información del negocio, reserva y el precio unitario.
    '''
    # Obtiene la reserva asociada al cliente actual o devuelve un error 404 si no existe
    reserva = get_object_or_404(Alquiler, id=reserva_id, cliente=request.user.cliente)
    negocio = Negocio.objects.first()

    # Calcular el precio unitario
    if reserva.cantidad_unidades > 0:
        precio_unitario = reserva.costo_total / reserva.cantidad_unidades
    else:
        precio_unitario = 0.00

    # Determinar el tipo de reserva: combo o servicio
    if reserva.combo:
        nombre_reserva = f"Combo: {reserva.combo.nombre}"
    elif reserva.servicio:
        nombre_reserva = f"Servicio: {reserva.servicio.titulo}"
    else:
        nombre_reserva = "Reserva sin especificar"

    # Crear el nombre del archivo PDF
    nombre_archivo = f"factura_{reserva.id}.pdf"

    # Contexto para la plantilla de la factura
    context = {
        'negocio': negocio,
        'reserva': reserva,
        'nombre_reserva': nombre_reserva,
        'fecha_emision': datetime.now().strftime('%d/%m/%Y'),
        'total': reserva.costo_total,
        'precio_unitario': round(precio_unitario, 2),
    }

    # Renderiza la plantilla HTML y genera el PDF
    html_string = render_to_string('facturas/factura_template.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
    with tempfile.NamedTemporaryFile(delete=True) as temp_file:
        HTML(string=html_string).write_pdf(temp_file.name)
        temp_file.seek(0)
        response.write(temp_file.read())
    return response


# Función auxiliar para convertir fechas
def convertir_fecha(fecha_str):
    ''' 
    Convierte una cadena de fecha en formato 'AAAA-MM-DD' a un objeto `date`.
    Retorna None si el formato es inválido.
    '''
    try:
        return parse_date(fecha_str)
    except (ValueError, TypeError):
        return None


# Vista específica para reporte por rol
def reporte_por_rol(request, rol=None):
    ''' 
    Genera un reporte de clientes filtrado por rol y rango de fechas.
    Devuelve el total de clientes que coinciden con los filtros.
    '''
    fecha_inicio = request.GET.get('fechaInicio')
    fecha_fin = request.GET.get('fechaFin')

    filtros = {}
    if fecha_inicio:
        filtros['fecha_registro__gte'] = convertir_fecha(fecha_inicio)
    if fecha_fin:
        filtros['fecha_registro__lte'] = convertir_fecha(fecha_fin)
    if rol:
        filtros['usuario__rol'] = rol

    total = Cliente.objects.filter(**filtros).count()
    return JsonResponse({'total': total})


# Vista específica para reporte de ventas
def reporte_ventas(request):
    ''' 
    Genera un reporte de las ventas totales en un rango de fechas.
    Devuelve el total de ventas en formato JSON.
    '''
    fecha_inicio = request.GET.get('fechaInicio')
    fecha_fin = request.GET.get('fechaFin')

    filtros = {}
    if fecha_inicio:
        filtros['fecha_hora_reserva__gte'] = convertir_fecha(fecha_inicio)
    if fecha_fin:
        filtros['fecha_hora_reserva__lte'] = convertir_fecha(fecha_fin)

    total_ventas = Alquiler.objects.filter(**filtros).aggregate(total=Sum('costo_total'))['total'] or 0
    return JsonResponse({'total': total_ventas})


# Vista específica para reporte de nuevos clientes
def reporte_nuevos_clientes(request):
    ''' 
    Genera un reporte de nuevos clientes registrados en un rango de fechas.
    Devuelve el total de nuevos clientes en formato JSON.
    '''
    fecha_inicio = request.GET.get('fechaInicio')
    fecha_fin = request.GET.get('fechaFin')

    if not (fecha_inicio and fecha_fin):
        return JsonResponse({'error': 'Debe proporcionar fechaInicio y fechaFin para nuevos clientes'}, status=400)

    fecha_inicio = convertir_fecha(fecha_inicio)
    fecha_fin = convertir_fecha(fecha_fin)

    if not (fecha_inicio and fecha_fin):
        return JsonResponse({'error': 'Formato de fecha inválido. Use AAAA-MM-DD'}, status=400)

    total = Cliente.objects.filter(fecha_registro__range=[fecha_inicio, fecha_fin]).count()
    return JsonResponse({'total': total})


# Vista para descargar reportes
def descargar_reporte(request, tipo):
    ''' 
    Permite descargar un reporte en formato JSON según el tipo especificado.
    Tipos disponibles: 'clientes', 'dueños', 'administradores', 'ventas', 'nuevos_clientes'.
    '''
    if tipo == 'clientes':
        return reporte_por_rol(request, rol='cliente')
    elif tipo == 'dueños':
        return reporte_por_rol(request, rol='dueño')
    elif tipo == 'administradores':
        return reporte_por_rol(request, rol='administrador')
    elif tipo == 'ventas':
        return reporte_ventas(request)
    elif tipo == 'nuevos_clientes':
        return reporte_nuevos_clientes(request)
    else:
        return JsonResponse({'error': 'Tipo de reporte no válido'}, status=400)
