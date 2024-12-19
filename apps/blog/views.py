import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import ComentarioForm, PublicacionForm
from .models import ImagenPublicacion, Publicacion

logger = logging.getLogger(__name__)


def blog(request):
    '''
    Muestra una lista paginada de todas las publicaciones del blog,
    ordenadas por fecha de creación en orden descendente.
    '''
    publicaciones_lista = Publicacion.objects.all().order_by('-fecha_creacion')
    paginator = Paginator(publicaciones_lista, 3)
    page_number = request.GET.get('page')
    publicaciones = paginator.get_page(page_number)

    return render(request, 'blog/blog.html', {'publicaciones': publicaciones})


def detalle_publicacion(request, pk):
    '''
    Muestra los detalles de una publicación específica y permite agregar comentarios.
    También incrementa el contador de visualizaciones si el usuario está autenticado.
    '''
    publicacion = get_object_or_404(Publicacion, pk=pk)
    comentarios = publicacion.comentarios.all().order_by('-fecha_creacion')

    # Contabilizar visualización solo si el usuario está autenticado
    if request.user.is_authenticated:
        session_key = f'viewed_publicacion_{publicacion.id}'
        if not request.session.get(session_key, False):
            publicacion.visualizaciones += 1
            publicacion.save()
            request.session[session_key] = True

    # Gestionar comentarios si se envía un formulario POST
    if request.method == 'POST' and request.user.is_authenticated:
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.publicacion = publicacion
            comentario.autor = request.user
            comentario.save()
            return redirect('detalle_publicacion', pk=publicacion.pk)
    else:
        form = ComentarioForm()

    # Verificar si la publicación fue editada
    fue_editada = publicacion.fecha_edicion is not None

    context = {
        'publicacion': publicacion,
        'comentarios': comentarios,
        'form': form,
        'fue_editada': fue_editada,
    }
    return render(request, 'blog/detalle_publicacion.html', context)


@login_required
def agregar_comentario(request, pk):
    '''
    Permite a un usuario autenticado agregar un comentario a una publicación específica.
    '''
    publicacion = get_object_or_404(Publicacion, pk=pk)
    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.autor = request.user
            comentario.publicacion = publicacion
            comentario.save()
            messages.success(request, 'Comentario agregado exitosamente.')
        else:
            messages.error(request, 'Error al agregar el comentario.')
    return redirect('detalle_publicacion', pk=pk)


@login_required
@require_POST
def like_publicacion(request, pk):
    '''
    Permite a un usuario dar o quitar "Me Gusta" a una publicación específica.
    '''
    publicacion = get_object_or_404(Publicacion, pk=pk)

    # Alternar el estado del "Me Gusta"
    if publicacion.me_gustas.filter(id=request.user.id).exists():
        publicacion.quitar_me_gusta(request.user)
        messages.success(request, "Has quitado tu 'Me Gusta'.")
    else:
        publicacion.agregar_me_gusta(request.user)
        messages.success(request, "Has dado 'Me Gusta' a esta publicación.")

    return redirect('detalle_publicacion', pk=pk)


@login_required
def crear_publicacion(request):
    '''
    Permite a un usuario con rol de "dueño" crear una nueva publicación,
    incluyendo la posibilidad de subir múltiples imágenes.
    '''
    if request.method == 'POST':
        form = PublicacionForm(request.POST, request.FILES)
        if form.is_valid():
            publicacion = form.save(commit=False)
            publicacion.autor = request.user
            publicacion.save()

            # Manejar múltiples imágenes manualmente
            imagenes = request.FILES.getlist('imagenes')
            for imagen in imagenes:
                ImagenPublicacion.objects.create(publicacion=publicacion, imagen=imagen)

            messages.success(request, 'Publicación creada exitosamente.')
            return redirect('blog')
        else:
            messages.error(request, 'Error al crear la publicación. Revisa los campos e intenta nuevamente.')
    else:
        form = PublicacionForm()

    return render(request, 'blog/crear_publicacion.html', {'form': form})


@login_required
def editar_publicacion(request, pk):
    '''
    Permite a un usuario con rol de "dueño" editar una publicación existente.
    '''
    publicacion = get_object_or_404(Publicacion, pk=pk)

    if request.user.rol != 'dueño':
        messages.error(request, "No tienes permiso para editar esta publicación.")
        return redirect('gestor_publicaciones')

    if request.method == 'POST':
        form = PublicacionForm(request.POST, request.FILES, instance=publicacion)
        if form.is_valid():
            publicacion = form.save(commit=False)
            publicacion.fecha_edicion = timezone.now()
            publicacion.save()
            messages.success(request, "La publicación ha sido actualizada correctamente.")
            return redirect('gestor_publicaciones')
    else:
        form = PublicacionForm(instance=publicacion)

    return render(request, 'blog/editar_publicacion.html', {'form': form, 'publicacion': publicacion})


@login_required
def eliminar_publicacion(request, pk):
    '''
    Permite a un usuario con rol de "dueño" eliminar una publicación existente.
    '''
    publicacion = get_object_or_404(Publicacion, pk=pk)

    if request.user.rol != 'dueño':
        messages.error(request, "No tienes permiso para eliminar esta publicación.")
        return redirect('gestor_publicaciones')

    publicacion.delete()
    messages.success(request, "La publicación ha sido eliminada correctamente.")
    return redirect('gestor_publicaciones')


@login_required
def gestor_publicaciones(request):
    '''
    Muestra una lista de publicaciones para que un usuario con rol de "dueño" pueda gestionarlas.
    '''
    if request.user.rol != 'dueño':
        messages.error(request, "No tienes permiso para acceder al gestor de publicaciones.")
        return redirect('pagina_principal')

    publicaciones = Publicacion.objects.all().order_by('-fecha_creacion')
    return render(request, 'blog/gestor_publicacion_blog.html', {'publicaciones': publicaciones})


@login_required
def eliminar_imagen_galeria(request, imagen_id):
    '''
    Permite a un usuario eliminar una imagen específica de una publicación.
    '''
    imagen = get_object_or_404(ImagenPublicacion, id=imagen_id)
    publicacion = imagen.publicacion
    imagen.delete()
    return redirect('blog/editar_publicacion', pk=publicacion.id)


