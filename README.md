
# Sistema de Gestión de Eventos

Este es un sistema de gestión de eventos dinámico, diseñado para permitir a empresas gestionar sus reservas de servicios y alquileres de forma eficiente. Incluye diferentes niveles de usuario (Administrador, Cliente, Dueño) y funcionalidades adaptadas a cada rol.

## Tecnologías Utilizadas

### Backend
- **Django 5.1.3**: Framework principal para el desarrollo del backend.
- **Django Channels**: Para manejo de aplicaciones en tiempo real.
- **Cloudinary**: Almacenamiento y manejo de archivos multimedia.
- **Gunicorn**: Servidor WSGI para despliegue.
- **SQLite/PostgreSQL**: Base de datos relacional.
  
### Frontend
- **HTML5**: Estructura de las páginas.
- **CSS3**: Estilización de la interfaz.
- **JavaScript**: Interactividad dinámica.
- **Bootstrap**: Framework CSS para diseño responsivo.

### Otras Dependencias
```
asgiref==3.8.1
Brotli==1.1.0
channels==4.2.0
cloudinary==1.41.0
django-cloudinary-storage==0.3.0
django-environ==0.11.2
pillow==10.4.0
psycopg2-binary==2.9.9
weasyprint==63.0
gunicorn==21.2.0
```

---

## Aplicaciones y Funcionalidades

### 1. **Administrador**
- **Funcionalidad**: Permite gestionar la información básica de la empresa (horarios, datos de contacto, etc.).
- **Archivos**: `models.py`, `views.py`, `forms.py`, `urls.py`, `templates`.

### 2. **Blog**
- **Funcionalidad**: Gestión de publicaciones y noticias relacionadas con los eventos.
- **Archivos**: `models.py`, `views.py`, `forms.py`, `urls.py`, `templates`.

### 3. **Clientes**
- **Funcionalidad**: Interfaz para que los clientes puedan realizar reservas de servicios o alquileres.
- **Archivos**: `models.py`, `views.py`, `urls.py`, `templates`.

### 4. **Dueño**
- **Funcionalidad**: Permite gestionar servicios, paquetes, y aspectos relacionados con los eventos.
- **Archivos**: `models.py`, `views.py`, `forms.py`, `urls.py`, `templates`.

### 5. **Reportes**
- **Funcionalidad**: Generación y visualización de reportes.
- **Archivos**: `models.py`, `views.py`, `urls.py`, `templates`.

### 6. **Reservas**
- **Funcionalidad**: Gestión de reservas de los clientes.
- **Archivos**: `models.py`, `views.py`, `urls.py`, `templates`.

### 7. **Servicios**
- **Funcionalidad**: Creación y gestión de servicios ofrecidos.
- **Archivos**: `models.py`, `views.py`, `forms.py`, `urls.py`, `templates`.

### 8. **Usuarios**
- **Funcionalidad**: Autenticación y gestión de perfiles de usuario.
- **Archivos**: `models.py`, `views.py`, `forms.py`, `urls.py`, `templates`.

---

## Instalación y Ejecución

1. **Clonar el Repositorio**

   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd gestor_eventos-main
   ```

2. **Crear el Entorno Virtual**

   ```bash
   python -m venv venv
   source venv/bin/activate    # En Windows: venv\Scripts\activate
   ```

3. **Instalar Dependencias**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar Variables de Entorno**

   Crear un archivo `.env` en la raíz del proyecto:

   ```env
   SECRET_KEY=tu_secreto
   DEBUG=True
   ```

5. **Aplicar Migraciones**

   ```bash
   python manage.py migrate
   ```

6. **Ejecutar el Servidor**

   ```bash
   python manage.py runserver
   ```

7. **Acceder a la Aplicación**

   Abrir [http://localhost:8000](http://localhost:8000) en el navegador.

---

## Capturas de Pantalla

- **Imagen Principal**:  
  ![Vista Principal](https://i.imgur.com/ejemplo_principal.png)

- **Interfaz de Administrador**:  
  ![Administrador](https://github.com/usuario/repositorio/blob/main/static/images/admin.png)

- **Interfaz de Cliente**:  
  ![Cliente](https://res.cloudinary.com/tu_cuenta/image/upload/v123456789/cliente.png)

- **Interfaz de Dueño**:  
  ![Dueño](https://i.imgur.com/ejemplo_dueño.png)

---

## Licencia

Este proyecto está licenciado bajo la **MIT License**.
