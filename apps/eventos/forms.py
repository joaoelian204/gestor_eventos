from django import forms

from .models import Evento, TipoEvento


class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ['tipo_evento', 'descripcion', 'valor_referencial', 'numero_horas_permitidas', 'valor_extra_hora']
        widgets = {
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'valor_referencial': forms.NumberInput(attrs={'class': 'form-control'}),
            'numero_horas_permitidas': forms.NumberInput(attrs={'class': 'form-control'}),
            'valor_extra_hora': forms.NumberInput(attrs={'class': 'form-control'}),
            'tipo_evento': forms.Select(attrs={'class': 'form-select'}),
        }

class TipoEventoForm(forms.ModelForm):
    class Meta:
        model = TipoEvento
        fields = ['nombre', 'descripcion', 'categoria', 'tipo_publico']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'categoria': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_publico': forms.TextInput(attrs={'class': 'form-control'}),
        }