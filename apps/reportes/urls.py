from django.urls import path

from . import views

urlpatterns = [
    path('facturas/generar/<int:reserva_id>/', views.generar_factura_pdf, name='generar_factura_pdf'),
    path('reportes/', views.generar_reporte, name='generar_reporte'),
    path('reportes/exportar/', views.exportar_reporte, name='exportar_reporte'),
    path('reportes/exportar_pdf/', views.exportar_reporte_pdf, name='exportar_reporte_pdf'),
    path('usuarios/', views.reporte_usuarios, name='reporte_usuarios'),
    path('usuarios/exportar/pdf/', views.exportar_reporte_usuarios_pdf, name='exportar_reporte_usuarios_pdf'),
    path('usuarios/exportar/excel/', views.exportar_reporte_usuarios_excel, name='exportar_reporte_usuarios_excel'),
    path('admins_duenos/', views.reporte_admins_duenos, name='reporte_admins_duenos'),
    path('admins_duenos/exportar/excel/', views.exportar_reporte_admins_duenos_excel, name='exportar_reporte_admins_duenos_excel'),
    path('admins_duenos/exportar/pdf/', views.exportar_reporte_admins_duenos_pdf, name='exportar_reporte_admins_duenos_pdf'),
]
