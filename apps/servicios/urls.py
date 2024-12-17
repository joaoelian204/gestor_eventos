from django.urls import path

from . import views

urlpatterns = [
    path('', views.lista_servicios, name='lista_servicios'),
    path('crear/', views.crear_servicio, name='crear_servicio'),
    path('<int:servicio_id>/editar/', views.editar_servicio, name='editar_servicio'),
    path('<int:servicio_id>/eliminar/', views.eliminar_servicio, name='eliminar_servicio'),
    path('crear-combo/', views.crear_combo, name='crear_combo'),
    path('combos/editar/<int:combo_id>/', views.editar_combo, name='editar_combo'),
    path('combos/eliminar/<int:combo_id>/', views.eliminar_combo, name='eliminar_combo'),
    path('combos/detalle/<int:combo_id>/', views.detalle_combo, name='detalle_combo'),
]
