from django import forms
from django.core.validators import EmailValidator, RegexValidator, URLValidator

from .models import Negocio


class NegocioForm(forms.ModelForm):
    # Validadores personalizados
    nombre_validator = RegexValidator(
        regex=r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$',
        message="El nombre solo puede contener letras y espacios."
    )
    telefono_validator = RegexValidator(
        regex=r'^\+?\d{7,15}$',
        message="El número de teléfono debe ser válido, puede incluir el código de país."
    )

    class Meta:
        model = Negocio
        fields = [
            'nombre', 'direccion_principal', 'direccion_secundaria',
            'telefono', 'email', 'logo', 'facebook', 'instagram', 'twitter'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion_principal': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'direccion_secundaria': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'facebook': forms.URLInput(attrs={'class': 'form-control'}),
            'instagram': forms.URLInput(attrs={'class': 'form-control'}),
            'twitter': forms.URLInput(attrs={'class': 'form-control'}),
        }

    # Validación de cada campo
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if not nombre:
            raise forms.ValidationError("El nombre es obligatorio.")
        self.nombre_validator(nombre)
        return nombre

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if not telefono:
            raise forms.ValidationError("El número de teléfono es obligatorio.")
        self.telefono_validator(telefono)
        return telefono

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("El correo electrónico es obligatorio.")
        EmailValidator()(email)
        return email

    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if logo and logo.size > 5 * 1024 * 1024:  # Limita el tamaño a 5 MB
            raise forms.ValidationError("El archivo del logo no puede superar los 5 MB.")
        return logo

    def clean_facebook(self):
        facebook = self.cleaned_data.get('facebook')
        if facebook:
            URLValidator()(facebook)
        return facebook

    def clean_instagram(self):
        instagram = self.cleaned_data.get('instagram')
        if instagram:
            URLValidator()(instagram)
        return instagram

    def clean_twitter(self):
        twitter = self.cleaned_data.get('twitter')
        if twitter:
            URLValidator()(twitter)
        return twitter
