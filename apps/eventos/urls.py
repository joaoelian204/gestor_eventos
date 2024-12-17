from django.urls import path

from . import views

urlpatterns = [
    # URLs para Tipos de Eventos
    path('tipos-eventos/', views.lista_tipo_eventos, name='lista_tipo_eventos'),
    path('tipos-eventos/crear/', views.crear_tipo_evento, name='crear_tipo_evento'),
    path('tipos-eventos/<int:tipo_evento_id>/editar/', views.editar_tipo_evento, name='editar_tipo_evento'),
    path('tipos-eventos/<int:tipo_evento_id>/eliminar/', views.eliminar_tipo_evento, name='eliminar_tipo_evento'),

    # URLs para Eventos
    path('eventos/', views.lista_eventos, name='lista_eventos'),
    path('eventos/crear/', views.crear_evento, name='crear_evento'),
    path('eventos/<int:evento_id>/editar/', views.editar_evento, name='editar_evento'),
    path('eventos/<int:evento_id>/eliminar/', views.eliminar_evento, name='eliminar_evento'),
]
