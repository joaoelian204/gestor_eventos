from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from apps.blog.models import Publicacion
from apps.clientes.models import Cliente
from apps.eventos.models import Evento
from apps.reservas.models import Alquiler
from apps.servicios.models import Combo, Servicio


# Verifica si el usuario es dueño
def es_dueño(user):
    return user.is_authenticated and user.rol == 'dueño'

@user_passes_test(es_dueño)
def dashboard(request):
    # Filtrar las reservas con estado 'confirmado' o 'finalizado' para calcular las ganancias
    reservas_confirmadas = Alquiler.objects.filter(estado__in=['confirmado', 'finalizado'])
    ganancias = sum(reserva.costo_total for reserva in reservas_confirmadas)

    # Contar registros de cada modelo
    total_reservas = Alquiler.objects.count()
    total_eventos = Evento.objects.count()
    total_servicios = Servicio.objects.count()
    total_publicaciones = Publicacion.objects.count()
    total_combos = Combo.objects.count()

    # Contexto para pasar a la plantilla
    context = {
        'ganancias': ganancias,
        'total_reservas': total_reservas,
        'total_eventos': total_eventos,
        'total_servicios': total_servicios,
        'total_publicaciones': total_publicaciones,
        'total_combos': total_combos,
    }

    return render(request, 'dueño/dashboard.html', context)

@user_passes_test(es_dueño)
def gestion_reservas(request):
    # Actualizar el estado y observación si se recibe una solicitud POST
    if request.method == 'POST':
        try:
            reserva_id = request.POST.get('reserva_id')
            nuevo_estado = request.POST.get('estado')
            observacion = request.POST.get('observacion')
            
            reserva = get_object_or_404(Alquiler, id=reserva_id)
            
            if nuevo_estado:
                reserva.estado = nuevo_estado
            if observacion:
                reserva.observacion = observacion
            
            reserva.save()
            messages.success(request, 'La reserva se actualizó correctamente.')
            return redirect('gestion_reservas')
        
        except Exception as e:
            messages.error(request, f'Ocurrió un error al actualizar la reserva: {str(e)}')
            return redirect('gestion_reservas')
    
    # Obtener todas las reservas
    reservas_list = Alquiler.objects.all().order_by('-fecha_hora_reserva')
    paginator = Paginator(reservas_list, 10)
    page_number = request.GET.get('page')
    reservas = paginator.get_page(page_number)

    return render(request, 'dueño/gestion_reservas.html', {'reservas': reservas})

@user_passes_test(es_dueño)
def gestion_eventos(request):
    eventos = Evento.objects.all()
    return render(request, 'dueño/gestion_eventos.html', {'eventos': eventos})


@user_passes_test(es_dueño)
def configuraciones_generales(request):
    if request.method == 'POST':
        # Aquí puedes agregar lógica para actualizar configuraciones
        pass
    return render(request, 'dueño/configuraciones_generales.html')

def gestionar_clientes(request):
    clientes_list = Cliente.objects.all()
    paginator = Paginator(clientes_list, 10)
    page_number = request.GET.get('page')
    clientes = paginator.get_page(page_number)
    return render(request, 'dueño/gestionar_clientes.html', {'clientes': clientes})
