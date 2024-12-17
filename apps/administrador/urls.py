from django.urls import path

from . import views

urlpatterns = [
    path('configuracion/', views.configuracion_negocio, name='configuracion_negocio'),
    path('vista-previa/', views.vista_previa_cliente, name='vista_previa_cliente'),
    path('dueños/crear/', views.crear_dueño, name='crear_dueño'),
    path('dueños/', views.lista_duenos, name='lista_duenos'),
    path('dueños/editar/<int:pk>/', views.editar_dueno, name='editar_dueno'),
    path('dueños/eliminar/<int:pk>/', views.eliminar_dueno, name='eliminar_dueno'),
]
