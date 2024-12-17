from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render

from .models import Negocio


# Helper: Verifica si el usuario es administrador
def es_administrador(user):
    """
    Verifica si el usuario autenticado tiene el rol de administrador.
    """
    return user.is_authenticated and hasattr(user, 'rol') and user.rol == 'administrador'


# CONFIGURACIÓN DEL NEGOCIO
@user_passes_test(es_administrador, login_url='login', redirect_field_name=None)
def configuracion_negocio(request):
    negocio, _ = Negocio.objects.get_or_create(id=1)

    if request.method == 'POST':
        negocio.nombre = request.POST.get('nombre', negocio.nombre)
        negocio.direccion_principal = request.POST.get('direccion_principal', negocio.direccion_principal)
        negocio.direccion_secundaria = request.POST.get('direccion_secundaria', negocio.direccion_secundaria)
        negocio.telefono = request.POST.get('telefono', negocio.telefono)
        negocio.correo = request.POST.get('correo', negocio.correo)

        # Procesar redes sociales
        redes_sociales = {
            "facebook": request.POST.get('redes_sociales[facebook]', negocio.redes_sociales.get('facebook', '')),
            "instagram": request.POST.get('redes_sociales[instagram]', negocio.redes_sociales.get('instagram', '')),
            "twitter": request.POST.get('redes_sociales[twitter]', negocio.redes_sociales.get('twitter', ''))
        }
        negocio.redes_sociales = redes_sociales

        # Procesar logo
        if 'logo' in request.FILES:
            negocio.logo = request.FILES['logo']

        # Validar y guardar
        try:
            negocio.full_clean()  # Valida todos los campos
            negocio.save()
            messages.success(request, "Configuración actualizada exitosamente.")
        except ValidationError as e:
            for field, errors in e.message_dict.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return render(request, 'administrador/configuracion.html', {'negocio': negocio})

        # Redirige a la vista previa
        return redirect('vista_previa_cliente')

    return render(request, 'administrador/configuracion.html', {'negocio': negocio})


@user_passes_test(es_administrador, login_url='login', redirect_field_name=None)
def vista_previa_cliente(request):
    """
    Muestra la vista previa de los datos del negocio.
    """
    negocio = Negocio.objects.first()  # Asumimos que siempre habrá un negocio registrado
    if negocio.redes_sociales is None:
        negocio.redes_sociales = {}  # Asegurarnos de que redes_sociales no sea None
    return render(request, 'administrador/vista_previa.html', {'negocio': negocio})


# CRUD DE DUEÑOS
@user_passes_test(es_administrador, login_url='login', redirect_field_name=None)
def crear_dueño(request):
    """
    Permite crear un nuevo usuario con rol de 'dueño'.
    Verifica la unicidad del nombre de usuario y correo electrónico.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Validación de unicidad
        if get_user_model().objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya está en uso. Por favor, elige otro.")
            return redirect('crear_dueño')

        if get_user_model().objects.filter(email=email).exists():
            messages.error(request, "El correo electrónico ya está registrado. Por favor, usa otro.")
            return redirect('crear_dueño')

        try:
            # Crear usuario con rol de dueño
            get_user_model().objects.create_user(
                username=username,
                email=email,
                password=password,
                rol='dueño'
            )
            messages.success(request, 'Dueño creado exitosamente.')
            return redirect('lista_duenos')
        except IntegrityError:
            messages.error(request, "Error: Ya existe un usuario con estos datos.")
        except Exception as e:
            messages.error(request, f"Ocurrió un error inesperado: {str(e)}")

    return render(request, 'administrador/crear_dueño.html')


@user_passes_test(es_administrador, login_url='login', redirect_field_name=None)
def lista_duenos(request):
    """
    Muestra una lista de todos los dueños registrados.
    """
    User = get_user_model()
    duenos = User.objects.filter(rol='dueño')
    return render(request, 'administrador/lista_duenos.html', {'duenos': duenos})


@user_passes_test(es_administrador, login_url='login', redirect_field_name=None)
def editar_dueno(request, pk):
    """
    Permite editar un dueño existente. Valida que los campos únicos (username y email) 
    no sean duplicados con otros usuarios.
    """
    User = get_user_model()
    dueno = get_object_or_404(User, pk=pk, rol='dueño')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')

        # Validar que el username no esté en uso por otro usuario
        if User.objects.filter(username=username).exclude(pk=pk).exists():
            messages.error(request, "El nombre de usuario ya está en uso.")
            return redirect('editar_dueno', pk=pk)

        # Validar que el email no esté en uso por otro usuario
        if User.objects.filter(email=email).exclude(pk=pk).exists():
            messages.error(request, "El correo electrónico ya está registrado. Por favor, usa otro.")
            return redirect('editar_dueno', pk=pk)

        # Actualizar datos del dueño
        dueno.username = username
        dueno.email = email
        dueno.save()
        messages.success(request, "Dueño actualizado exitosamente.")
        return redirect('lista_duenos')

    return render(request, 'administrador/editar_dueno.html', {'dueno': dueno})



@user_passes_test(es_administrador, login_url='login', redirect_field_name=None)
def eliminar_dueno(request, pk):
    """
    Permite eliminar un dueño existente después de confirmar la acción.
    """
    User = get_user_model()
    dueno = get_object_or_404(User, pk=pk, rol='dueño')

    if request.method == 'POST':
        dueno.delete()
        messages.success(request, "Dueño eliminado exitosamente.")
        return redirect('lista_duenos')

    return render(request, 'administrador/eliminar_dueno.html', {'dueno': dueno})
