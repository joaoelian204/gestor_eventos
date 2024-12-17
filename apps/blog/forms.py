from django import forms
from django.core.exceptions import ValidationError
from PIL import Image  # Biblioteca para trabajar con imágenes

from .models import Comentario, Publicacion


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


# Función de validación para los formatos de imagen permitidos
def validate_image_format(file):
    # Amplía la lista de extensiones permitidas
    allowed_extensions = ['jpeg', 'jpg', 'png', 'gif', 'webp', 'bmp', 'tiff', 'svg']
    try:
        img = Image.open(file)
        img_format = img.format.lower()
        print(f"Formato de imagen detectado: {img_format}")  # Depuración
        if img_format not in allowed_extensions:
            raise ValidationError(f"El archivo '{file.name}' no es una imagen válida. Se permiten los formatos: {', '.join(allowed_extensions)}.")
    except Exception as e:
        raise ValidationError(f"Error al procesar el archivo '{file.name}': {e}")


# Formulario para Publicaciones
class PublicacionForm(forms.ModelForm):
    imagen_principal = forms.ImageField(
        required=False,
        label='Imagen Principal',
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        validators=[validate_image_format]
    )

    class Meta:
        model = Publicacion
        fields = ['titulo', 'contenido', 'imagen_principal']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título de la publicación'}),
            'contenido': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Contenido de la publicación'}),
        }
        labels = {
            'titulo': 'Título',
            'contenido': 'Contenido',
        }

# Formulario para Comentarios
class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['contenido']
        widgets = {
            'contenido': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Escribe tu comentario aquí...',
                'class': 'form-control'
            }),
        }
        labels = {
            'contenido': '',
        }
        help_texts = {
            'contenido': 'Escribe tu comentario aquí...',
        }

    def clean_contenido(self):
        contenido = self.cleaned_data.get('contenido')
        if not contenido or contenido.strip() == "":
            raise ValidationError("El comentario no puede estar vacío.")
        return contenido
