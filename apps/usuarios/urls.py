from django.urls import path

from . import views

urlpatterns = [
    path('registro/', views.registro_usuario, name='registro_usuario'),
    path('activar/<uidb64>/<token>/', views.activar_cuenta, name='activar_cuenta'),
    path('completar-registro/', views.completar_registro, name='completar_registro'),
    path('login/', views.login_usuario, name='login_usuario'),
    path('logout/', views.logout_usuario, name='logout_usuario'),
    path('recuperar-contrasena/', views.recuperar_contrasena, name='recuperar_contrasena'),
    path('recuperar-usuario/', views.recuperar_usuario, name='recuperar_usuario'),
    path('resetear-contrasena/<uidb64>/<token>/', views.resetear_contrasena, name='resetear_contrasena'),
]


