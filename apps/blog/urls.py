from django.urls import path

from . import views

urlpatterns = [
    path('', views.blog, name='blog'),
    path('crear/', views.crear_publicacion, name='crear_publicacion'),
    path('<int:pk>/', views.detalle_publicacion, name='detalle_publicacion'),
    path('<int:pk>/comentar/', views.agregar_comentario, name='agregar_comentario'),
    path('publicacion/<int:pk>/like/', views.like_publicacion, name='like_publicacion'),
    path('publicacion/<int:pk>/editar/', views.editar_publicacion, name='editar_publicacion'),
    path('publicacion/<int:pk>/eliminar/', views.eliminar_publicacion, name='eliminar_publicacion'),
    path('gestor-publicaciones/', views.gestor_publicaciones, name='gestor_publicaciones'),
    path('imagen/<int:imagen_id>/eliminar/', views.eliminar_imagen_galeria, name='eliminar_imagen_galeria'),
]
