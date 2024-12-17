from cloudinary.models import CloudinaryField
from django.conf import settings
from django.db import models


class Publicacion(models.Model):
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_edicion = models.DateTimeField(null=True, blank=True)
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    imagen_principal = CloudinaryField('publicaciones', null=True, blank=True)
    visualizaciones = models.PositiveIntegerField(default=0)
    me_gustas = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='publicaciones_likeadas', blank=True)  # Relación con usuarios

    def __str__(self):
        return self.titulo

    def agregar_me_gusta(self, user):
        """Agrega un 'Me Gusta' del usuario."""
        self.me_gustas.add(user)

    def quitar_me_gusta(self, user):
        """Quita un 'Me Gusta' del usuario."""
        self.me_gustas.remove(user)

    @property
    def total_me_gustas(self):
        """Devuelve el total de 'Me Gusta'."""
        return self.me_gustas.count()


class ImagenPublicacion(models.Model):
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE, related_name='galeria')
    descripcion = models.CharField(max_length=255, null=True, blank=True)
    imagen = CloudinaryField('publicaciones/galeria')

    def __str__(self):
        return f"Imagen de {self.publicacion.titulo}"


class Comentario(models.Model):
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comentario de {self.autor} en {self.publicacion}"
