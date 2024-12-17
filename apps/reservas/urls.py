from django.urls import path

from . import views

urlpatterns = [
    path('reservas/', views.listar_reservas, name='listar_reservas'),
    path('crear_alquiler/', views.crear_alquiler, name='crear_alquiler'),
    path('<int:reserva_id>/detalle/', views.detalle_reserva, name='detalle_reserva'),
    path('<int:reserva_id>/editar/', views.editar_reserva, name='editar_reserva'),
    path('<int:reserva_id>/eliminar/', views.eliminar_reserva, name='eliminar_reserva'),
]

