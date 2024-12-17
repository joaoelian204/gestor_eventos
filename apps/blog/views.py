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
    # Obtener todas las publicaciones ordenadas por fecha de creación descendente
    publicaciones_lista = Publicacion.objects.all().order_by('-fecha_creacion')
    
    # Crear un paginador para dividir en grupos de 9 publicaciones
    paginator = Paginator(publicaciones_lista, 3)
    
    # Obtener el número de página de la solicitud GET (por defecto será la página 1)
    page_number = request.GET.get('page')
    
    # Obtener el objeto de la página actual
    publicaciones = paginator.get_page(page_number)

    return render(request, 'blog/blog.html', {'publicaciones': publicaciones})

def detalle_publicacion(request, pk):
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
    publicacion = get_object_or_404(Publicacion, pk=pk)

    # Verificar si el usuario está autenticado
    if not request.user.is_authenticated:
        messages.error(request, "Debes iniciar sesión o registrarte para dar 'Me Gusta'.")
        return redirect('login_usuario')

    # Alternar el estado del "Me Gusta"
    if publicacion.me_gustas.filter(id=request.user.id).exists():
        publicacion.quitar_me_gusta(request.user)
        messages.success(request, "Has quitado tu 'Me Gusta'.")
    else:
        publicacion.agregar_me_gusta(request.user)
        messages.success(request, "Has dado 'Me Gusta' a esta publicación.")

    # Redirigir al detalle de la publicación
    return redirect('detalle_publicacion', pk=pk)

# Crear una nueva publicación (solo para usuarios con rol "dueño")
@login_required
def crear_publicacion(request):
    if request.method == 'POST':
        print("Recibiendo datos del formulario...")
        print(f"Archivos en request.FILES: {request.FILES}")

        form = PublicacionForm(request.POST, request.FILES)
        if form.is_valid():
            publicacion = form.save(commit=False)
            publicacion.autor = request.user
            publicacion.save()
            print(f"Publicación '{publicacion.titulo}' guardada correctamente.")

            # Manejar múltiples imágenes manualmente
            imagenes = request.FILES.getlist('imagenes')
            if imagenes:
                for imagen in imagenes:
                    ImagenPublicacion.objects.create(publicacion=publicacion, imagen=imagen)
                    print(f"Imagen guardada: {imagen.name}")
            else:
                print("No se recibieron imágenes adicionales.")

            messages.success(request, 'Publicación creada exitosamente.')
            return redirect('blog')
        else:
            print(f"Errores del formulario: {form.errors}")
            messages.error(request, 'Error al crear la publicación. Revisa los campos e intenta nuevamente.')
    else:
        form = PublicacionForm()

    return render(request, 'blog/crear_publicacion.html', {'form': form})

@login_required
def editar_publicacion(request, pk):
    publicacion = get_object_or_404(Publicacion, pk=pk)

    # Verificar si el usuario es el dueño del negocio
    if request.user.rol != 'dueño':
        messages.error(request, "No tienes permiso para editar esta publicación. Solo el dueño puede realizar esta acción.")
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
    publicacion = get_object_or_404(Publicacion, pk=pk)

    # Verificar si el usuario es el dueño del negocio
    if request.user.rol != 'dueño':
        messages.error(request, "No tienes permiso para eliminar esta publicación. Solo el dueño puede realizar esta acción.")
        return redirect('gestor_publicaciones')

    publicacion.delete()
    messages.success(request, "La publicación ha sido eliminada correctamente.")
    return redirect('gestor_publicaciones')

@login_required
def gestor_publicaciones(request):
    # Verificar si el usuario es el dueño del negocio
    if request.user.rol != 'dueño':
        messages.error(request, "No tienes permiso para acceder al gestor de publicaciones.")
        return redirect('pagina_principal')

    # Obtener todas las publicaciones
    publicaciones = Publicacion.objects.all().order_by('-fecha_creacion')

    return render(request, 'blog/gestor_publicacion_blog.html', {'publicaciones': publicaciones})

@login_required
def eliminar_imagen_galeria(request, imagen_id):
    imagen = get_object_or_404(ImagenPublicacion, id=imagen_id)
    publicacion = imagen.publicacion
    imagen.delete()
    return redirect('blog/editar_publicacion', pk=publicacion.id)

