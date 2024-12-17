from django.urls import path

from gestion_eventos.views import pagina_principal

from . import views

urlpatterns = [
    path('', pagina_principal, name='pagina_principal'),
    path('catalogo/', views.catalogo_servicios, name='catalogo_servicios'),
    path('reservas/', views.reservas_activas, name='reservas_activas'),
    path('historial/', views.historial_reservas, name='historial_reservas'),
    path('perfil-cliente/', views.perfil_cliente, name='perfil_cliente'),
    path('detalle-combo/<int:combo_id>/', views.detalle_combo, name='detalle_combo'),
    path('editar-perfil/', views.editar_perfil_cliente, name='editar_perfil_cliente'),
    path('cambiar-contrasena/', views.cambiar_contrasena_cliente, name='cambiar_contrasena_cliente'),
]