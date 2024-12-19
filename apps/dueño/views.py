from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from apps.blog.models import Publicacion
from apps.clientes.models import Cliente
from apps.reservas.models import Alquiler
from apps.servicios.models import Combo, Servicio


# Verifica si el usuario es dueño
def es_dueño(user):
    ''' 
    Verifica si el usuario está autenticado y tiene el rol de 'dueño'.
    Retorna True si el usuario es dueño, de lo contrario, False.
    '''
    return user.is_authenticated and user.rol == 'dueño'


@user_passes_test(es_dueño)
def dashboard(request):
    ''' 
    Muestra el panel de control para el usuario dueño con estadísticas generales, 
    como las ganancias totales, el número de reservas, servicios, publicaciones y combos.
    '''
    # Filtra las reservas confirmadas o finalizadas
    reservas_confirmadas = Alquiler.objects.filter(estado__in=['confirmado', 'finalizado'])
    
    # Calcula las ganancias sumando el costo total de las reservas confirmadas
    ganancias = sum(reserva.costo_total for reserva in reservas_confirmadas)
    
    # Obtiene los totales de reservas, servicios, publicaciones y combos
    total_reservas = Alquiler.objects.count()
    total_servicios = Servicio.objects.count()
    total_publicaciones = Publicacion.objects.count()
    total_combos = Combo.objects.count()

    # Contexto que se enviará a la plantilla
    context = {
        'ganancias': ganancias,
        'total_reservas': total_reservas,
        'total_servicios': total_servicios,
        'total_publicaciones': total_publicaciones,
        'total_combos': total_combos,
    }

    # Renderiza la plantilla 'dashboard.html' con el contexto
    return render(request, 'dueño/dashboard.html', context)


@user_passes_test(es_dueño)
def gestion_reservas(request):
    ''' 
    Gestiona las reservas permitiendo actualizar el estado y agregar observaciones. 
    Además, muestra una lista paginada de las reservas, ordenadas por estado y fecha.
    '''
    # Si el método es POST, se actualiza la reserva
    if request.method == 'POST':
        reserva_id = request.POST.get('reserva_id')
        nuevo_estado = request.POST.get('estado')
        observacion = request.POST.get('observacion')
        
        # Obtiene la reserva o devuelve un error 404 si no existe
        reserva = get_object_or_404(Alquiler, id=reserva_id)
        
        # Actualiza el estado y la observación si se proporcionan
        if nuevo_estado:
            reserva.estado = nuevo_estado
        if observacion:
            reserva.observacion = observacion
        
        # Guarda los cambios en la base de datos
        reserva.save()
        messages.success(request, 'La reserva se actualizó correctamente.')
        
        # Redirecciona a la misma vista después de actualizar
        return redirect('gestion_reservas')

    # Define la prioridad de los estados para ordenarlos
    estado_prioridad = {
        'en_curso': 1,
        'pendiente': 2,
        'finalizado': 3,
    }

    # Obtiene todas las reservas y las ordena por estado y fecha
    reservas_list = Alquiler.objects.all().order_by(
        'estado',
        '-fecha_hora_reserva'
    )

    # Aplica prioridad al estado para ordenar manualmente
    reservas_list = sorted(reservas_list, key=lambda reserva: estado_prioridad.get(reserva.estado, 4))

    # Pagina la lista de reservas (4 por página)
    paginator = Paginator(reservas_list, 4)
    page_number = request.GET.get('page')
    reservas = paginator.get_page(page_number)

    # Renderiza la plantilla 'gestion_reservas.html' con la lista paginada de reservas
    return render(request, 'dueño/gestion_reservas.html', {'reservas': reservas})


def gestionar_clientes(request):
    ''' 
    Muestra una lista paginada de los clientes registrados en el sistema.
    '''
    # Obtiene todos los clientes
    clientes_list = Cliente.objects.all()
    
    # Pagina la lista de clientes (10 por página)
    paginator = Paginator(clientes_list, 10)
    page_number = request.GET.get('page')
    clientes = paginator.get_page(page_number)
    
    # Renderiza la plantilla 'gestionar_clientes.html' con la lista paginada de clientes
    return render(request, 'dueño/gestionar_clientes.html', {'clientes': clientes})

