from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('enviar-configuracion/', views.enviar_configuracion, name='enviar_configuracion'),
    path('enviar-consumo/', views.enviar_consumo, name='enviar_consumo'),
    path('operaciones-sistema/', views.operaciones_sistema, name='operaciones_sistema'),
    path('inicializar-sistema/', views.inicializar_sistema, name='inicializar_sistema'),
    path('consultar-datos/', views.consultar_datos, name='consultar_datos'),
    path('crear-recurso/', views.crear_recurso, name='crear_recurso'),
    path('generar-factura/', views.generar_factura, name='generar_factura'),
    path('info-estudiante/', views.info_estudiante, name='info_estudiante'),
    path('ayuda/', views.ayuda, name='ayuda'),
]