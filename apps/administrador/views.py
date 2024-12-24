from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, RegexValidator, URLValidator
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render

from .models import Negocio


#Verifica si el usuario es administrador
def es_administrador(user):
    """
    Verifica si el usuario autenticado tiene el rol de administrador.
    """
    return user.is_authenticated and hasattr(user, 'rol') and user.rol == 'administrador'


# Validadores personalizados
nombre_validator = RegexValidator(
    regex=r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$',
    message="El nombre solo puede contener letras y espacios."
)
telefono_validator = RegexValidator(
    regex=r'^\+?\d{7,15}$',
    message="El número de teléfono debe ser válido, puede incluir el código de país."
)
url_validator = URLValidator(message="Debe ser una URL válida.")
email_validator = EmailValidator(message="Debe ser un correo electrónico válido.")

@user_passes_test(es_administrador, login_url='login', redirect_field_name=None)
def configuracion_negocio(request):
    negocio, _ = Negocio.objects.get_or_create(id=1)

    # Almacenamos si hay errores para prevenir la actualización en caso de errores
    errors = []

    if request.method == 'POST':
        # Validar y actualizar campos individuales
        nombre = request.POST.get('nombre', negocio.nombre)
        try:
            nombre_validator(nombre)
            negocio.nombre = nombre
        except ValidationError as e:
            errors.append(f"Nombre: {e.message}")

        direccion_principal = request.POST.get('direccion_principal', negocio.direccion_principal)
        negocio.direccion_principal = direccion_principal

        direccion_secundaria = request.POST.get('direccion_secundaria', negocio.direccion_secundaria)
        negocio.direccion_secundaria = direccion_secundaria

        telefono = request.POST.get('telefono', negocio.telefono)
        try:
            telefono_validator(telefono)
            negocio.telefono = telefono
        except ValidationError as e:
            errors.append(f"Teléfono: {e.message}")

        correo = request.POST.get('correo', negocio.correo)
        try:
            email_validator(correo)
            negocio.correo = correo
        except ValidationError as e:
            errors.append(f"Correo: {e.message}")

        # Procesar redes sociales
        redes_sociales = {}
        for red in ['facebook', 'instagram', 'twitter']:
            url = request.POST.get(f'redes_sociales[{red}]', negocio.redes_sociales.get(red, ''))
            try:
                if url:  # Validar solo si se proporciona una URL
                    url_validator(url)
                redes_sociales[red] = url
            except ValidationError as e:
                errors.append(f"{red.capitalize()}: {e.message}")

        negocio.redes_sociales = redes_sociales

        # Procesar logo
        if 'logo' in request.FILES:
            negocio.logo = request.FILES['logo']

        # Si hay errores, no actualizamos el negocio y mostramos los errores
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'administrador/configuracion.html', {'negocio': negocio})

        # Validar y guardar solo si no hay errores
        try:
            negocio.full_clean()  # Validaciones del modelo
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
    negocio = Negocio.objects.first()
    if negocio.redes_sociales is None:
        negocio.redes_sociales = {}
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
