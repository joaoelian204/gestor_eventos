from cloudinary.exceptions import Error as CloudinaryError
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from apps.servicios.forms import ComboForm, ServicioForm
from apps.servicios.models import Combo, ImagenCombo, Servicio


def es_dueño(user):
    """Verifica si el usuario es dueño."""
    return user.is_authenticated and user.rol == 'dueño'


@user_passes_test(es_dueño)
def lista_servicios(request):
    """Lista todos los servicios disponibles en el sistema, incluidos los combos"""
    servicios = Servicio.objects.all()
    combos = Combo.objects.all()

    # Aplicamos filtros si están presentes
    titulo = request.GET.get('titulo', '')
    tipo_servicio = request.GET.get('tipo_servicio', '')
    precio_max = request.GET.get('precio_max', None)

    if titulo:
        servicios = servicios.filter(titulo__icontains=titulo)
        combos = combos.filter(nombre__icontains=titulo)
    
    if tipo_servicio:
        servicios = servicios.filter(tipo_servicio=tipo_servicio)
    
    if precio_max:
        servicios = servicios.filter(valor_por_unidad__lte=precio_max)
    
    # Pasamos los servicios y combos al contexto
    context = {
        'servicios': servicios,
        'combos': combos,
    }
    
    return render(request, 'servicios/lista_servicios.html', context)

@user_passes_test(es_dueño)
def crear_servicio(request):
    if request.method == 'POST':
        form = ServicioForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Servicio creado con éxito.")
                return redirect('lista_servicios')
            except CloudinaryError as e:
                messages.error(request, f"Error al subir la imagen: {e}")
        else:
            messages.error(request, "Por favor, corrige los errores del formulario.")
    else:
        form = ServicioForm()

    return render(request, 'servicios/crear_servicio.html', {'form': form})

@user_passes_test(es_dueño)
def editar_servicio(request, servicio_id):
    servicio = get_object_or_404(Servicio, id=servicio_id)
    if request.method == 'POST':
        form = ServicioForm(request.POST, request.FILES, instance=servicio)
        if form.is_valid():
            form.save()
            messages.success(request, "Servicio actualizado con éxito.")
            return redirect('lista_servicios')
        else:
            messages.error(request, "Por favor, corrige los errores del formulario.")
    else:
        form = ServicioForm(instance=servicio)

    return render(request, 'servicios/editar_servicio.html', {'form': form, 'servicio': servicio})


@user_passes_test(es_dueño)
def eliminar_servicio(request, servicio_id):
    """Elimina un servicio del sistema."""
    servicio = get_object_or_404(Servicio, id=servicio_id)
    servicio.delete()
    messages.success(request, "Servicio eliminado con éxito.")
    return redirect('lista_servicios')


@login_required
@user_passes_test(es_dueño)
def crear_combo(request):
    """Crea un combo con múltiples imágenes asociadas y servicios incluidos."""
    if request.method == 'POST':
        form = ComboForm(request.POST)
        if form.is_valid():
            # Guardar el combo sin las imágenes
            combo = form.save(commit=True)
            combo.servicios_incluidos.set(form.cleaned_data['servicios_incluidos'])

            # Guardar las imágenes asociadas
            imagenes = request.FILES.getlist('imagenes')
            if imagenes:
                for imagen in imagenes:
                    ImagenCombo.objects.create(combo=combo, imagen=imagen)

            messages.success(request, "Combo creado con éxito.")
            return redirect('lista_servicios')
        else:
            messages.error(request, "Error al crear el combo. Revisa el formulario.")
    else:
        form = ComboForm()

    return render(request, 'servicios/crear_combo.html', {'form': form})

@user_passes_test(es_dueño)
def editar_combo(request, combo_id):
    """Edita un combo existente."""
    combo = get_object_or_404(Combo, id=combo_id)
    if request.method == 'POST':
        form = ComboForm(request.POST, request.FILES, instance=combo)
        if form.is_valid():
            form.save()
            messages.success(request, "Combo actualizado con éxito.")
            return redirect('lista_servicios')
        else:
            messages.error(request, "Por favor, corrige los errores del formulario.")
    else:
        form = ComboForm(instance=combo)

    return render(request, 'servicios/editar_combo.html', {'form': form, 'combo': combo})


@user_passes_test(es_dueño)
def eliminar_combo(request, combo_id):
    """Elimina un combo del sistema."""
    combo = get_object_or_404(Combo, id=combo_id)
    if request.method == 'POST':
        combo.delete()
        messages.success(request, "Combo eliminado con éxito.")
        return redirect('lista_servicios')
    return render(request, 'servicios/eliminar_combo.html', {'combo': combo})


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
    
    return render(request, 'servicios/detalle_combo.html', context)