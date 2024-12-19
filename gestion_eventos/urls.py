from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from .views import pagina_principal

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', pagina_principal, name='pagina_principal'),
    path('usuarios/', include('apps.usuarios.urls')),
    path('administrador/', include('apps.administrador.urls')),
    path('dueño/', include('apps.dueño.urls')),
    path('servicios/', include('apps.servicios.urls')),
    path('reservas/', include('apps.reservas.urls')),
    path('reportes/', include('apps.reportes.urls')),
    path('clientes/', include('apps.clientes.urls')),
    path('blog/', include('apps.blog.urls')),
]

# Configuración para servir archivos de medios y estáticos en modo desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


