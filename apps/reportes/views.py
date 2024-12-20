import tempfile
from datetime import datetime

import pandas as pd
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.dateparse import parse_date
from weasyprint import HTML

from apps.administrador.models import Negocio
from apps.clientes.models import Cliente
from apps.reservas.models import Alquiler

User = get_user_model()


# Verifica si el usuario es dueño
def es_dueño(user):
    '''
    Verifica si el usuario está autenticado y tiene el rol de 'dueño'.
    Retorna True si el usuario es dueño, de lo contrario, False.
    '''
    return user.is_authenticated and user.rol == 'dueño'

#-------------- Facturas para cliente --------------#

# Generar factura en PDF para una reserva de combo o servicio
@login_required
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


#-------------- Reportes de ventas --------------#

# Generar reporte de ventas
@user_passes_test(es_dueño)
def generar_reporte(request):
    '''
    Genera un reporte de ventas con la lista de reservas finalizadas y el total de ventas.
    Permite filtrar por fecha de inicio y fin.'''
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    # Filtrar solo reservas finalizadas
    reservas = Alquiler.objects.filter(estado='finalizado')

    # Filtrado por fecha de inicio
    if fecha_inicio:
        try:
            fecha_inicio_dt = timezone.make_aware(datetime.strptime(fecha_inicio, '%Y-%m-%d'))
            reservas = reservas.filter(fecha_hora_reserva__gte=fecha_inicio_dt)
        except ValueError:
            fecha_inicio_dt = None

    # Filtrado por fecha de fin
    if fecha_fin:
        try:
            fecha_fin_dt = timezone.make_aware(datetime.strptime(fecha_fin, '%Y-%m-%d'))
            reservas = reservas.filter(fecha_hora_reserva__lte=fecha_fin_dt)
        except ValueError:
            fecha_fin_dt = None

    # Calcular el total de dinero recolectado
    total_recolectado = reservas.aggregate(Sum('costo_total'))['costo_total__sum'] or 0

    return render(request, 'reportes/reporte_ventas.html', {
        'reservas': reservas,
        'total_recolectado': total_recolectado,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin
    })


# Exportar reporte de ventas a Excel
@user_passes_test(es_dueño)
def exportar_reporte(request):
    '''
    Exporta un reporte de ventas a un archivo Excel.
    '''
    fecha_inicio = request.POST.get('fecha_inicio')
    fecha_fin = request.POST.get('fecha_fin')

    # Filtrar solo reservas finalizadas
    reservas = Alquiler.objects.filter(estado='finalizado')

    # Filtrado por fecha de inicio
    if fecha_inicio:
        fecha_inicio_dt = timezone.make_aware(datetime.strptime(fecha_inicio, '%Y-%m-%d'))
        reservas = reservas.filter(fecha_hora_reserva__gte=fecha_inicio_dt)

    # Filtrado por fecha de fin
    if fecha_fin:
        fecha_fin_dt = timezone.make_aware(datetime.strptime(fecha_fin, '%Y-%m-%d'))
        reservas = reservas.filter(fecha_hora_reserva__lte=fecha_fin_dt)

    # Crear DataFrame
    data = []
    for reserva in reservas:
        cliente_nombre = f"{reserva.cliente.nombres} {reserva.cliente.apellidos}" if reserva.cliente else "N/A"
        servicio_combo_nombre = reserva.servicio.titulo if reserva.servicio else (reserva.combo.nombre if reserva.combo else "N/A")

        data.append({
            'Cliente': cliente_nombre,
            'Servicio/Combo': servicio_combo_nombre,
            'Dirección': reserva.direccion,
            'Fecha Inicio': reserva.fecha_hora_reserva.strftime("%Y-%m-%d %H:%M"),
            'Fecha Fin': reserva.fecha_fin_reserva.strftime("%Y-%m-%d %H:%M") if reserva.fecha_fin_reserva else 'N/A',
            'Estado': reserva.estado,
            'Costo Total': f"${reserva.costo_total:.2f}",
        })

    # Crear respuesta de Excel
    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="reporte_ventas.xlsx"'

    with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Ventas')
        worksheet = writer.sheets['Ventas']
        worksheet.set_column('A:G', 20)

    return response


# Exportar reporte de ventas a PDF
@user_passes_test(es_dueño)
def exportar_reporte_pdf(request):
    '''
    Exporta un reporte en formato PDF con la lista de reservas finalizadas y el total de ventas.
    '''
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    # Filtrar solo reservas finalizadas
    reservas = Alquiler.objects.filter(estado='finalizado')

    # Filtrado por fecha de inicio
    if fecha_inicio:
        try:
            fecha_inicio_dt = timezone.make_aware(datetime.strptime(fecha_inicio, '%Y-%m-%d'))
            reservas = reservas.filter(fecha_hora_reserva__gte=fecha_inicio_dt)
        except ValueError:
            pass

    # Filtrado por fecha de fin
    if fecha_fin:
        try:
            fecha_fin_dt = timezone.make_aware(datetime.strptime(fecha_fin, '%Y-%m-%d'))
            reservas = reservas.filter(fecha_hora_reserva__lte=fecha_fin_dt)
        except ValueError:
            pass

    # Calcular total de ventas
    total_ventas = sum(reserva.costo_total for reserva in reservas)

    # Contexto para la plantilla
    context = {
        'reservas': reservas,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'fecha_generacion': timezone.now().strftime("%Y-%m-%d %H:%M"),
        'total_ventas': total_ventas,
    }

    # Renderizar la plantilla HTML
    html_string = render_to_string('reportes/reporte_ventas_pdf.html', context)

    # Generar el PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_ventas.pdf"'

    # Crear el PDF con WeasyPrint
    HTML(string=html_string).write_pdf(response)

    return response

#-------------- Reportes de usuarios --------------#

#funciones para reporte de usuarios
@user_passes_test(es_dueño)
def reporte_usuarios(request):
    '''
    Muestra un reporte con la lista de clientes registrados en el sistema.
    Permite filtrar por fecha de registro.'''
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    usuarios = User.objects.all()

    if fecha_inicio and fecha_fin:
        try:
            fecha_inicio_dt = timezone.make_aware(datetime.strptime(fecha_inicio, '%Y-%m-%d'))
            fecha_fin_dt = timezone.make_aware(datetime.strptime(fecha_fin, '%Y-%m-%d'))
            usuarios = usuarios.filter(date_joined__range=(fecha_inicio_dt, fecha_fin_dt))
        except ValueError:
            pass

    # Filtrar solo clientes
    clientes = Cliente.objects.filter(usuario__in=usuarios)

    return render(request, 'reportes/reporte_usuarios.html', {
        'clientes': clientes,
    })

#funciones para exportar reporte de usuarios a excel
@user_passes_test(es_dueño)
def exportar_reporte_usuarios_excel(request):
    '''
    Exporta un reporte de clientes a un archivo Excel.
    '''
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    clientes = Cliente.objects.all()

    if fecha_inicio and fecha_fin:
        fecha_inicio_dt = timezone.make_aware(datetime.strptime(fecha_inicio, '%Y-%m-%d'))
        fecha_fin_dt = timezone.make_aware(datetime.strptime(fecha_fin, '%Y-%m-%d'))
        clientes = clientes.filter(fecha_registro__range=(fecha_inicio_dt, fecha_fin_dt))

    # Crear DataFrame
    data = []
    for cliente in clientes:
        data.append({
            'Nombre': f"{cliente.nombres} {cliente.apellidos}",
            'Email': cliente.correo,
            'Fecha de Registro': cliente.fecha_registro.strftime("%Y-%m-%d %H:%M"),
        })

    df = pd.DataFrame(data)

    # Crear respuesta de Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="reporte_clientes.xlsx"'

    with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Clientes')
        worksheet = writer.sheets['Clientes']
        worksheet.set_column('A:C', 25)

    return response

#funciones para exportar reporte de usuarios a pdf
@user_passes_test(es_dueño)
def exportar_reporte_usuarios_pdf(request):
    '''
    Exporta un reporte en formato PDF con la lista de clientes registrados.
    '''
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    # Obtener solo los clientes
    clientes = Cliente.objects.all()

    # Filtrado por fecha de registro si se proporcionan fechas
    if fecha_inicio and fecha_fin:
        try:
            fecha_inicio_dt = timezone.make_aware(datetime.strptime(fecha_inicio, '%Y-%m-%d'))
            fecha_fin_dt = timezone.make_aware(datetime.strptime(fecha_fin, '%Y-%m-%d'))
            clientes = clientes.filter(fecha_registro__range=(fecha_inicio_dt, fecha_fin_dt))
        except ValueError:
            pass

    # Contexto para la plantilla
    context = {
        'clientes': clientes,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'fecha_generacion': timezone.now().strftime("%Y-%m-%d %H:%M"),
    }

    # Renderizar la plantilla HTML
    html_string = render_to_string('reportes/reporte_usuarios_pdf.html', context)

    # Generar el PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_usuarios.pdf"'

    # Crear el PDF con WeasyPrint
    HTML(string=html_string).write_pdf(response)

    return response

#-------------- Reportes de admins y dueños --------------#

#funciones para reporte de admins y dueños
@user_passes_test(es_dueño)
def reporte_admins_duenos(request):
    '''
    Muestra un reporte con la lista de administradores y dueños registrados en el sistema.
    Permite filtrar por fecha de registro.
    '''
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    usuarios = User.objects.exclude(is_superuser=False, is_staff=False)

    if fecha_inicio and fecha_fin:
        try:
            fecha_inicio_dt = timezone.make_aware(datetime.strptime(fecha_inicio, '%Y-%m-%d'))
            fecha_fin_dt = timezone.make_aware(datetime.strptime(fecha_fin, '%Y-%m-%d'))
            usuarios = usuarios.filter(date_joined__range=(fecha_inicio_dt, fecha_fin_dt))
        except ValueError:
            usuarios = User.objects.none()
    else:
        usuarios = User.objects.none()

    return render(request, 'reportes/reporte_admins_duenos.html', {
        'usuarios': usuarios,
    })

#funciones para exportar reporte de admins y dueños a excel
@user_passes_test(es_dueño)
def exportar_reporte_admins_duenos_excel(request):
    '''
    Exporta un reporte de administradores y dueños a un archivo Excel.
    '''
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    usuarios = User.objects.exclude(is_superuser=False, is_staff=False)

    if fecha_inicio and fecha_fin:
        try:
            fecha_inicio_dt = timezone.make_aware(datetime.strptime(fecha_inicio, '%Y-%m-%d'))
            fecha_fin_dt = timezone.make_aware(datetime.strptime(fecha_fin, '%Y-%m-%d'))
            usuarios = usuarios.filter(date_joined__range=(fecha_inicio_dt, fecha_fin_dt))
        except ValueError:
            usuarios = User.objects.none()

    data = []
    for user in usuarios:
        data.append({
            'ID': user.id,
            'Username': user.username,
            'Email': user.email,
            'Fecha de Registro': user.date_joined.strftime("%Y-%m-%d %H:%M"),
            'Rol': 'Administrador' if user.is_superuser else 'Dueño',
        })

    df = pd.DataFrame(data)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="reporte_admins_duenos.xlsx"'

    with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Admins y Dueños')
        worksheet = writer.sheets['Admins y Dueños']
        worksheet.set_column('A:E', 25)

    return response

#funciones para exportar reporte de admins y dueños a pdf
@user_passes_test(es_dueño)
def exportar_reporte_admins_duenos_pdf(request):
    '''
    Exporta un reporte en formato PDF con la lista de administradores y dueños registrados.
    '''
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    usuarios = User.objects.exclude(is_superuser=False, is_staff=False)

    if fecha_inicio and fecha_fin:
        try:
            fecha_inicio_dt = timezone.make_aware(datetime.strptime(fecha_inicio, '%Y-%m-%d'))
            fecha_fin_dt = timezone.make_aware(datetime.strptime(fecha_fin, '%Y-%m-%d'))
            usuarios = usuarios.filter(date_joined__range=(fecha_inicio_dt, fecha_fin_dt))
        except ValueError:
            usuarios = User.objects.none()

    context = {
        'usuarios': usuarios,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'fecha_generacion': timezone.now().strftime("%Y-%m-%d %H:%M"),
    }

    html_string = render_to_string('reportes/reporte_admins_duenos_pdf.html', context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_admins_duenos.pdf"'

    HTML(string=html_string).write_pdf(response)

    return response
