import secrets

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlencode, urlsafe_base64_decode, urlsafe_base64_encode

from apps.usuarios.forms import ClienteRegistroForm
from apps.usuarios.models import Usuario

# -------------------- Registro de Usuario --------------------
"""
Permite registrar un nuevo usuario en el sistema. Si el correo o nombre de usuario ya está registrado, se muestra un mensaje de error.
Envía un correo electrónico con un enlace de activación al usuario con un diseño elegante.
"""
def registro_usuario(request):
    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']

        if Usuario.objects.filter(email=email).exists():
            messages.error(request, 'El correo ya está registrado.')
            return render(request, 'usuarios/registro.html')

        if Usuario.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya está en uso.')
            return render(request, 'usuarios/registro.html')

        request.session['temp_user_data'] = {
            'username': username,
            'email': email,
            'password': password
        }

        token = secrets.token_urlsafe(16)
        request.session['temp_user_token'] = token

        query_params = urlencode({'token': token})
        link_activacion = request.build_absolute_uri(f"/usuarios/completar-registro/?{query_params}")

        mensaje_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: auto; border: 1px solid #ddd; padding: 20px; border-radius: 10px;">
                <h2 style="text-align: center; color: #007BFF;">Completa tu Registro</h2>
                <p>Hola <strong>{username}</strong>,</p>
                <p>Gracias por registrarte en nuestra plataforma. Para completar el registro, por favor haz clic en el siguiente enlace:</p>
                <p style="text-align: center;">
                    <a href="{link_activacion}" style="display: inline-block; padding: 10px 20px; font-size: 16px; color: #fff; background-color: #28a745; text-decoration: none; border-radius: 5px;">
                        Completar Registro
                    </a>
                </p>
                <p>Si el botón no funciona, también puedes copiar y pegar el siguiente enlace en tu navegador:</p>
                <p style="word-break: break-word; color: #555;">{link_activacion}</p>
                <p>Esperamos que disfrutes de la experiencia. Si tienes alguna pregunta, no dudes en contactarnos.</p>
                <p>Saludos,</p>
                <p>El equipo de soporte.</p>
            </div>
        </body>
        </html>
        """

        try:
            send_mail(
                subject='Completa tu Registro',
                message='',
                html_message=mensaje_html,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
            messages.success(request, 'Registro inicial exitoso. Revisa tu correo para continuar.')
            return redirect('completar_registro')
        except Exception:
            messages.error(request, 'No se pudo enviar el correo. Verifica tu conexión e intenta más tarde.')
            return redirect('registro_usuario')

    return render(request, 'usuarios/registro.html')


# -------------------- Activación de Cuenta --------------------
"""
Activa la cuenta de usuario al verificar el token de activación enviado por correo.
"""
def activar_cuenta(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Usuario.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, 'Cuenta activada. Completa tu perfil.')
        return redirect('completar_registro')
    else:
        return redirect('registro_usuario')


# -------------------- Completar Perfil --------------------
"""
Permite a los usuarios completar su perfil una vez que han activado su cuenta.
"""
def completar_registro(request):
    temp_user_data = request.session.get('temp_user_data')
    temp_user_token = request.session.get('temp_user_token')
    token = request.GET.get('token')

    if not temp_user_data or temp_user_token != token:
        messages.error(request, 'El enlace de registro no es válido o ha expirado.')
        return redirect('registro_usuario')

    if request.method == 'POST':
        form = ClienteRegistroForm(request.POST)
        if form.is_valid():
            try:
                user = Usuario.objects.create_user(
                    username=temp_user_data['username'],
                    email=temp_user_data['email'],
                    password=temp_user_data['password']
                )
                user.save()

                cliente = form.save(commit=False)
                cliente.usuario = user
                cliente.email = user.email
                cliente.save()

                request.session.pop('temp_user_data', None)
                request.session.pop('temp_user_token', None)

                messages.success(request, 'Perfil completado exitosamente.')
                return redirect('login_usuario')
            except Exception as e:
                print(e)  # Imprime el error en la consola
                messages.error(request, 'Ocurrió un error al completar el registro.')
        else:
            print(form.errors)  # Imprime los errores del formulario en la consola
    else:
        form = ClienteRegistroForm()

    return render(request, 'usuarios/completar_registro.html', {'form': form})


# -------------------- Login --------------------
"""
Permite a los usuarios iniciar sesión en el sistema. Verifica las credenciales.
"""
def login_usuario(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('pagina_principal' if user.is_authenticated else 'dashboard')
        else:
            messages.error(request, 'Credenciales inválidas.')
    return render(request, 'usuarios/login.html')


# -------------------- Logout --------------------
"""
Cierra la sesión del usuario autenticado.
"""
@login_required
def logout_usuario(request):
    logout(request)
    return redirect('login_usuario')



# -------------------- Recuperar Contraseña --------------------
"""
Envía un enlace al correo del usuario para restablecer su contraseña con un diseño elegante.
"""
def recuperar_contrasena(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = Usuario.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            link_reset = request.build_absolute_uri(
                reverse('resetear_contrasena', kwargs={'uidb64': uid, 'token': token})
            )

            # Plantilla HTML para el correo
            mensaje_html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: auto; border: 1px solid #ddd; padding: 20px; border-radius: 10px;">
                    <h2 style="text-align: center; color: #007BFF;">Restablecimiento de Contraseña</h2>
                    <p>Hola,</p>
                    <p>Hemos recibido una solicitud para restablecer tu contraseña. Si no realizaste esta solicitud, por favor ignora este mensaje.</p>
                    <p>Para restablecer tu contraseña, haz clic en el enlace siguiente:</p>
                    <p style="text-align: center;">
                        <a href="{link_reset}" style="display: inline-block; padding: 10px 20px; font-size: 16px; color: #fff; background-color: #007BFF; text-decoration: none; border-radius: 5px;">
                            Restablecer Contraseña
                        </a>
                    </p>
                    <p>Si el botón no funciona, también puedes copiar y pegar el siguiente enlace en tu navegador:</p>
                    <p style="word-break: break-word; color: #555;">{link_reset}</p>
                    <p>Gracias,</p>
                    <p>El equipo de soporte.</p>
                </div>
            </body>
            </html>
            """

            # Enviar correo de restablecimiento
            send_mail(
                subject='Restablecer Contraseña',
                message='',
                html_message=mensaje_html,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )

            messages.success(request, 'Hemos enviado un enlace para restablecer tu contraseña a tu correo.')
        except Usuario.DoesNotExist:
            messages.error(request, 'No existe un usuario registrado con este correo.')
        return redirect('recuperar_contrasena')
    return render(request, 'usuarios/recuperar_contrasena.html')


# -------------------- Resetear Contraseña --------------------
"""
Permite a los usuarios restablecer su contraseña después de validar el token.
"""
def resetear_contrasena(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Usuario.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            nueva_contrasena = request.POST.get('password')
            user.set_password(nueva_contrasena)
            user.save()
            messages.success(request, 'Tu contraseña se ha restablecido exitosamente.')
            return redirect('login_usuario')
        return render(request, 'usuarios/resetear_contrasena.html')
    else:
        messages.error(request, 'El enlace no es válido o ha expirado.')
        return redirect('recuperar_contrasena')


# -------------------- Crear Administrador --------------------
"""
Permite a los superusuarios crear nuevos administradores.
"""
# Validar si el usuario actual es superusuario
def es_superusuario(user):
    return user.is_authenticated and user.is_superuser

@user_passes_test(es_superusuario)
def crear_administrador(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Validaciones básicas
        if Usuario.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya existe.')
            return redirect('crear_administrador')

        if Usuario.objects.filter(email=email).exists():
            messages.error(request, 'El correo electrónico ya está registrado.')
            return redirect('crear_administrador')

        # Crear administrador
        Usuario.objects.create_user(username=username, email=email, password=password, rol='administrador', is_staff=True)
        messages.success(request, f'Administrador "{username}" creado exitosamente.')
        return redirect('lista_usuarios')

    return render(request, 'usuarios/crear_administrador.html')

def recuperar_usuario(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = Usuario.objects.get(email=email)
            # Plantilla HTML para el correo
            mensaje_html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: auto; border: 1px solid #ddd; padding: 20px; border-radius: 10px;">
                    <h2 style="text-align: center; color: #007BFF;">Recuperación de Nombre de Usuario</h2>
                    <p>Hola,</p>
                    <p>Hemos recibido una solicitud para recuperar tu nombre de usuario. Tu nombre de usuario es:</p>
                    <p style="text-align: center; font-size: 18px; font-weight: bold; color: #007BFF;">{user.username}</p>
                    <p>Si no realizaste esta solicitud, puedes ignorar este mensaje.</p>
                    <p>Gracias,</p>
                    <p>El equipo de soporte.</p>
                </div>
            </body>
            </html>
            """

            # Enviar correo con el nombre de usuario
            send_mail(
                subject='Recuperación de Nombre de Usuario',
                message='',
                html_message=mensaje_html,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )

            messages.success(request, 'Te hemos enviado un correo con tu nombre de usuario.')
        except Usuario.DoesNotExist:
            messages.error(request, 'No existe un usuario registrado con ese correo.')
        return redirect('login_usuario')
    return render(request, 'usuarios/recuperar_usuario.html')

