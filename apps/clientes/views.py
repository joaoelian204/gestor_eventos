from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.clientes.models import Cliente
from apps.reservas.models import Alquiler
from apps.servicios.models import Combo, ImagenCombo, Servicio


@login_required
def catalogo_servicios(request):
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
    """Muestra los detalles de un combo específico."""
    combo = get_object_or_404(Combo, id=combo_id)
    imagenes = ImagenCombo.objects.filter(combo=combo)
    servicios_incluidos = combo.servicios_incluidos.all()
    
    context = {
        'combo': combo,
        'imagenes': imagenes,
        'servicios_incluidos': servicios_incluidos,
    }
    
    return render(request, 'clientes/detalle_combo.html', context)


@login_required
def reservas_activas(request):
    # Obtén las reservas activas del cliente, excluyendo las reservas finalizadas
    reservas = Alquiler.objects.filter(cliente=request.user.cliente).exclude(estado='finalizado')

    return render(request, 'clientes/reservas_activas.html', {'reservas': reservas})


@login_required
def historial_reservas(request):
    # Obtén las reservas finalizadas del cliente
    historial = Alquiler.objects.filter(cliente=request.user.cliente, estado='finalizado')

    return render(request, 'clientes/historial_reservas.html', {'historial': historial})

@login_required
def perfil_cliente(request):
    cliente = request.user.cliente
    return render(request, 'clientes/perfil_cliente.html', {'cliente': cliente})

@login_required
def editar_perfil_cliente(request):
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
    

