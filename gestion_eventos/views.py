from django.shortcuts import redirect, render

from apps.administrador.models import Negocio
from apps.servicios.models import Servicio


def pagina_principal(request):
    # Verifica si el usuario está autenticado
    if request.user.is_authenticated:
        # Redirección según el rol del usuario
        rol = getattr(request.user, 'rol', None)

        if rol == 'administrador':
            return redirect('configuracion_negocio')
        elif rol == 'dueño':
            return redirect('dashboard')
        elif rol == 'cliente':
            negocio = Negocio.objects.first()
            servicios = Servicio.objects.all()
            return render(request, 'pagina_principal.html', {'negocio': negocio, 'servicios': servicios})

    # Usuarios no autenticados
    negocio = Negocio.objects.first()
    servicios = Servicio.objects.all()
    return render(request, 'pagina_principal.html', {'negocio': negocio, 'servicios': servicios})


