from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.clientes.models import Cliente
from apps.reservas.models import Alquiler
from apps.servicios.models import Combo, ImagenCombo, Servicio


@login_required
def catalogo_servicios(request):
    '''
    Muestra el catálogo de servicios y combos disponibles.
    Permite filtrar por búsqueda de texto y por tipo (servicio o combo).
    '''
    query = request.GET.get('q')
    tipo = request.GET.get('tipo')

    servicios = Servicio.objects.all()
    combos = Combo.objects.all()

    if query:
        servicios = servicios.filter(titulo__icontains=query)
        combos = combos.filter(nombre__icontains=query)

    if tipo == 'servicio':
        items = list(servicios)
    elif tipo == 'combo':
        items = list(combos)
    else:
        items = list(servicios) + list(combos)

    items.sort(key=lambda x: x.titulo if hasattr(x, 'titulo') else x.nombre)

    # Obtener el cliente asociado al usuario actual
    try:
        cliente = request.user.cliente
    except Cliente.DoesNotExist:
        cliente = None

    return render(request, 'clientes/catalogo_servicios.html', {
        'items': items,
        'cliente': cliente
    })
    

def detalle_combo(request, combo_id):
    ''' 
    Muestra los detalles de un combo específico, incluyendo imágenes y servicios incluidos.
    '''
    combo = get_object_or_404(Combo, id=combo_id)
    imagenes = ImagenCombo.objects.filter(combo=combo)
    servicios_incluidos = combo.servicios_incluidos.all()
    
    # Capturar el cliente_id desde los parámetros GET
    cliente_id = request.GET.get('cliente_id')

    context = {
        'combo': combo,
        'imagenes': imagenes,
        'servicios_incluidos': servicios_incluidos,
        'cliente_id': cliente_id, 
    }
    
    return render(request, 'clientes/detalle_combo.html', context)


@login_required
def reservas_activas(request):
    ''' 
    Muestra una lista paginada de las reservas activas del cliente actual.
    Excluye las reservas finalizadas y las ordena por fecha descendente.
    '''
    reservas_list = Alquiler.objects.filter(
        cliente=request.user.cliente
    ).exclude(
        estado='finalizado'
    ).order_by('-fecha_hora_reserva')

    # Pagina las reservas (8 por página)
    paginator = Paginator(reservas_list, 8)
    page_number = request.GET.get('page')
    reservas = paginator.get_page(page_number)

    return render(request, 'clientes/reservas_activas.html', {'reservas': reservas})


@login_required
def historial_reservas(request):
    ''' 
    Muestra una lista paginada del historial de reservas finalizadas del cliente actual.
    Las reservas se muestran desde la más reciente a la más antigua.
    '''
    historial_list = Alquiler.objects.filter(
        cliente=request.user.cliente,
        estado='finalizado'
    ).order_by('-fecha_hora_reserva')

    # Pagina el historial de reservas (8 por página)
    paginator = Paginator(historial_list, 8)
    page_number = request.GET.get('page')
    reservas = paginator.get_page(page_number)

    return render(request, 'clientes/historial_reservas.html', {'reservas': reservas})

@login_required
def perfil_cliente(request):
    ''' 
    Muestra el perfil del cliente actual.
    '''
    cliente = request.user.cliente
    return render(request, 'clientes/perfil_cliente.html', {'cliente': cliente})

@login_required
def editar_perfil_cliente(request):
    ''' 
    Permite al cliente editar su información personal como nombres, apellidos, identificación, correo, teléfono, etc.
    '''
    cliente = request.user.cliente
    if request.method == 'POST':
        cliente.nombres = request.POST.get('nombres')
        cliente.apellidos = request.POST.get('apellidos')
        cliente.identificacion = request.POST.get('identificacion')
        cliente.correo = request.POST.get('correo')
        cliente.telefono = request.POST.get('telefono')
        cliente.nacionalidad = request.POST.get('nacionalidad')
        cliente.genero = request.POST.get('genero')

        cliente.save()
        messages.success(request, 'Tu perfil se ha actualizado exitosamente.')
        return redirect('perfil_cliente')

    return render(request, 'clientes/perfil_cliente.html', {'cliente': cliente})


@login_required
def cambiar_contrasena_cliente(request):
    ''' 
    Permite al cliente cambiar su contraseña. 
    Se verifica que las contraseñas coincidan y que cumplan con los requisitos de seguridad.
    '''
    if request.method == 'POST':
        nueva_contrasena = request.POST.get('password').strip()
        confirmar_contrasena = request.POST.get('confirm_password').strip()

        if nueva_contrasena != confirmar_contrasena:
            messages.error(request, 'Las contraseñas no coinciden.')
        elif len(nueva_contrasena) < 8 or not any(char.isdigit() for char in nueva_contrasena) or not any(char.isalpha() for char in nueva_contrasena):
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres y contener números y letras.')
        else:
            request.user.set_password(nueva_contrasena)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Tu contraseña se ha actualizado exitosamente.')

        return redirect('perfil_cliente')
    
    


