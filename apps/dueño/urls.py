from django.urls import path

from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('gestion-reservas/', views.gestion_reservas, name='gestion_reservas'),
    path('clientes/', views.gestionar_clientes, name='gestionar_clientes'),
    path('configuraciones/', views.configuraciones_generales, name='configuraciones_generales'),
]




