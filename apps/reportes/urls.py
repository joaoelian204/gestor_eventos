from django.urls import path

from . import views

urlpatterns = [
    # Generar factura PDF
    path('generar_factura/<int:reserva_id>/', views.generar_factura_pdf, name='generar_factura_pdf'),

    # Reportes por rol
    path('reporte/<str:rol>/', views.reporte_por_rol, name='reporte_por_rol'),

    # Reportes específicos
    path('reporte/ventas/', views.reporte_ventas, name='reporte_ventas'),
    path('reporte/nuevos_clientes/', views.reporte_nuevos_clientes, name='reporte_nuevos_clientes'),

    # Descargar reportes
    path('reporte/<str:tipo>/descargar/', views.descargar_reporte, name='descargar_reporte'),
]
