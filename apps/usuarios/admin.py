
from django import forms
from django.contrib import admin
from django.utils.timezone import now

from .models import Usuario


# Formulario personalizado para administradores
class AdministradorForm(forms.ModelForm):
     '''
    Clase para definir un formulario personalizado que se usará para crear usuarios con rol de administrador.
    '''
    class Meta:
        '''
        Meta información del formulario, especificando el modelo asociado y los campos a incluir.
        '''
        model = Usuario
        fields = ['username', 'email', 'password']  # Campos necesarios

    # Mostrar contraseña en texto plano al crear
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")

    def save(self, commit=True):
        '''
        Guarda el usuario con el rol de administrador y configura la contraseña encriptada.
        '''
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # Encriptar la contraseña
        user.rol = 'administrador'  # Establecer el rol como "administrador"
        user.is_staff = True        # Marcar como staff
        user.is_superuser = False   # No superusuario por defecto
        if commit:
            user.save()
        return user


# Personalización del modelo de administrador
class UsuarioAdmin(admin.ModelAdmin):
    '''
    Clase para personalizar cómo se muestra el modelo Usuario en la interfaz de administración.
    '''
    form = AdministradorForm
    list_display = ('username', 'email', 'fecha_creacion', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('username', 'email')

    def save_model(self, request, obj, form, change):
        '''
        Guarda el modelo Usuario en la base de datos. Si es una nueva instancia, asigna la fecha de creación.
        '''
        if not obj.pk:  # Si el usuario se está creando por primera vez
            obj.fecha_creacion = now()  # Establecer la fecha de creación
        super().save_model(request, obj, form, change)

# Registro del modelo Usuario en el sitio de administración
admin.site.register(Usuario, UsuarioAdmin)
