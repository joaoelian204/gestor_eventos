from django import template

register = template.Library()

@register.filter
def alert_color(tag):
    colors = {
        "success": "linear-gradient(135deg, #28a745, #85e085)",  # Verde
        "error": "linear-gradient(135deg, #dc3545, #f5b5b5)",   # Rojo
        "warning": "linear-gradient(135deg, #ffc107, #ffe5a3)", # Amarillo
        "info": "linear-gradient(135deg, #17a2b8, #a8e0e6)"     # Azul
    }
    return colors.get(tag, "linear-gradient(135deg, #6c757d, #d6d8db)")  # Gris por defecto
