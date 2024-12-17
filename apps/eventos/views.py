from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EventoForm, TipoEventoForm
from .models import Evento, TipoEvento


# Verifica si el usuario es dueño
def es_dueño(user):
    return user.is_authenticated and user.rol == 'dueño'

@user_passes_test(es_dueño)
def lista_eventos(request):
    eventos = Evento.objects.all()
    return render(request, 'eventos/lista_eventos.html', {'eventos': eventos})

@user_passes_test(es_dueño)
def crear_evento(request):
    if request.method == 'POST':
        form = EventoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Evento creado exitosamente.")
            return redirect('lista_eventos')
        else:
            messages.error(request, "Por favor, corrige los errores del formulario.")
    else:
        form = EventoForm()
    return render(request, 'eventos/crear_evento.html', {'form': form})

@user_passes_test(es_dueño)
def editar_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    if request.method == 'POST':
        form = EventoForm(request.POST, instance=evento)
        if form.is_valid():
            form.save()
            messages.success(request, "Evento actualizado exitosamente.")
            return redirect('lista_eventos')
        else:
            messages.error(request, "Por favor, corrige los errores del formulario.")
    else:
        form = EventoForm(instance=evento)
    return render(request, 'eventos/editar_evento.html', {'form': form, 'evento': evento})

@user_passes_test(es_dueño)
def eliminar_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    if request.method == 'POST':
        evento.delete()
        messages.success(request, "Evento eliminado exitosamente.")
        return redirect('lista_eventos')
    return render(request, 'eventos/eliminar_evento.html', {'evento': evento})

@user_passes_test(es_dueño)
def lista_tipo_eventos(request):
    tipos_eventos = TipoEvento.objects.all()
    return render(request, 'eventos/lista_tipo_eventos.html', {'tipos_eventos': tipos_eventos})

@user_passes_test(es_dueño)
def crear_tipo_evento(request):
    if request.method == 'POST':
        form = TipoEventoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Tipo de evento creado exitosamente.")
            return redirect('lista_tipo_eventos')
    else:
        form = TipoEventoForm()
    return render(request, 'eventos/crear_tipo_evento.html', {'form': form})

@user_passes_test(es_dueño)
def editar_tipo_evento(request, tipo_evento_id):
    tipo_evento = get_object_or_404(TipoEvento, id=tipo_evento_id)
    if request.method == 'POST':
        form = TipoEventoForm(request.POST, instance=tipo_evento)
        if form.is_valid():
            form.save()
            messages.success(request, "Tipo de evento actualizado exitosamente.")
            return redirect('lista_tipo_eventos')
    else:
        form = TipoEventoForm(instance=tipo_evento)
    return render(request, 'eventos/editar_tipo_evento.html', {'form': form, 'tipo_evento': tipo_evento})

@user_passes_test(es_dueño)
def eliminar_tipo_evento(request, tipo_evento_id):
    tipo_evento = get_object_or_404(TipoEvento, id=tipo_evento_id)
    if request.method == 'POST':
        tipo_evento.delete()
        messages.success(request, "Tipo de evento eliminado exitosamente.")
        return redirect('lista_tipo_eventos')
    return render(request, 'eventos/eliminar_tipo_evento.html', {'tipo_evento': tipo_evento})