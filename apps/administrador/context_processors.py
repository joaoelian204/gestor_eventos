from .models import Negocio


def negocio_context(request):
    negocio = Negocio.objects.first()
    return {'negocio': negocio}
