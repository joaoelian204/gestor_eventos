from django import forms

from .models import Negocio


class NegocioForm(forms.ModelForm):
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
            'facebook': forms.URLInput(attrs={'class': 'form-control'}),
            'instagram': forms.URLInput(attrs={'class': 'form-control'}),
            'twitter': forms.URLInput(attrs={'class': 'form-control'}),
        }
