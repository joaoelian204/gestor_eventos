from django import forms

from apps.servicios.models import Combo, ImagenCombo, Servicio


class MultipleFileInput(forms.ClearableFileInput):
    """Widget personalizado para permitir múltiples archivos."""
    allow_multiple_selected = True

    def __init__(self, attrs=None):
        attrs = {'multiple': True, **(attrs or {})}
        super().__init__(attrs)
        
class ServicioForm(forms.ModelForm):
    """Formulario para crear y editar un servicio individual"""

    class Meta:
        model = Servicio
        fields = ['titulo', 'descripcion', 'valor_por_unidad', 'tipo_servicio', 'imagen_referencial']

    def clean_valor_por_unidad(self):
        valor = self.cleaned_data.get('valor_por_unidad')
        if valor <= 0:
            raise forms.ValidationError("El valor por unidad debe ser mayor que cero.")
        return valor

    def clean_titulo(self):
        titulo = self.cleaned_data.get('titulo')
        if not titulo:
            raise forms.ValidationError("El título del servicio es obligatorio.")
        return titulo


class ComboForm(forms.ModelForm):
    """Formulario para crear y editar un combo."""

    class Meta:
        model = Combo
        fields = ['nombre', 'descripcion', 'precio', 'servicios_incluidos']

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio <= 0:
            raise forms.ValidationError("El precio del combo debe ser mayor que cero.")
        return precio


class ImagenComboForm(forms.ModelForm):
    """Formulario para gestionar las imágenes de un combo"""

    class Meta:
        model = ImagenCombo
        fields = ['imagen', 'descripcion']

    def clean_imagen(self):
        imagen = self.cleaned_data.get('imagen')
        if not imagen:
            raise forms.ValidationError("Se debe cargar al menos una imagen.")
        return imagen
