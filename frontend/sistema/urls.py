from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('enviar-configuracion/', views.enviar_configuracion, name='enviar_configuracion'),
    path('enviar-consumo/', views.enviar_consumo, name='enviar_consumo'),
    path('operaciones-sistema/', views.operaciones_sistema, name='operaciones_sistema'),
    path('inicializar_sistema/', views.inicializar_sistema, name='inicializar_sistema'),
    path('consultar-datos/', views.consultar_datos, name='consultar_datos'),
    path('crear-datos/', views.crear_datos, name='crear_datos'),
    path('crear-recurso/', views.crear_recurso, name='crear_recurso'),
    path('crear-categoria/', views.crear_categoria, name='crear_categoria'),
    path('crear-configuracion/', views.crear_configuracion, name='crear_configuracion'),
    path('crear-cliente/', views.crear_cliente, name='crear_cliente'),
    path('crear-instancia/', views.crear_instancia, name='crear_instancia'),
    path('proceso-facturacion/', views.proceso_facturacion, name='proceso_facturacion'),
    path('generar-factura/', views.generar_factura, name='generar_factura'),
    path('reportes-pdf/', views.reportes_pdf, name='reportes_pdf'),
    path('generar-pdf/', views.generar_pdf, name='generar_pdf'),
    path('info-estudiante/', views.info_estudiante, name='info_estudiante'),
    path('ayuda/', views.ayuda, name='ayuda'),
]