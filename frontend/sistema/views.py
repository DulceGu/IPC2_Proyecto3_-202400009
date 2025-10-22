from django.shortcuts import render

import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings

def index(request):
    return render(request, 'index.html')

def enviar_configuracion(request):
    if request.method == 'POST' and request.FILES.get('archivo'):
        archivo = request.FILES['archivo']
        
        try:
            response = requests.post(
                f'{settings.BACKEND_URL}/cargarConfiguracion',
                files={'file': archivo}
            )
            return JsonResponse(response.json())
        except Exception as e:
            return JsonResponse({
                'mensaje': f'Error al enviar configuración: {str(e)}',
                'status': 500
            })
    
    return render(request, 'enviar_configuracion.html')

def enviar_consumo(request):
    if request.method == 'POST' and request.FILES.get('archivo'):
        archivo = request.FILES['archivo']
        
        try:
            response = requests.post(
                f'{settings.BACKEND_URL}/cargarConsumos',
                files={'file': archivo}
            )
            return JsonResponse(response.json())
        except Exception as e:
            return JsonResponse({
                'mensaje': f'Error al enviar consumos: {str(e)}',
                'status': 500
            })
    
    return render(request, 'enviar_consumo.html')

def operaciones_sistema(request):
    return render(request, 'operaciones_sistema.html')

def inicializar_sistema(request):
    if request.method == 'POST':
        try:
            response = requests.post(f'{settings.BACKEND_URL}/reset')
            return JsonResponse(response.json())
        except Exception as e:
            return JsonResponse({
                'mensaje': f'Error al inicializar sistema: {str(e)}',
                'status': 500
            })
    
    return JsonResponse({'mensaje': 'Método no permitido', 'status': 405})

def consultar_datos(request):
    if request.method == 'GET':
        tipo = request.GET.get('tipo', 'todos')
        
        try:
            response = requests.get(f'{settings.BACKEND_URL}/consultarDatos?tipo={tipo}')
            return JsonResponse(response.json())
        except Exception as e:
            return JsonResponse({
                'mensaje': f'Error al consultar datos: {str(e)}',
                'status': 500
            })
    
    return JsonResponse({'mensaje': 'Método no permitido', 'status': 405})

def crear_recurso(request):
    if request.method == 'POST':
        try:
            data = {
                'id': request.POST.get('id'),
                'nombre': request.POST.get('nombre'),
                'abreviatura': request.POST.get('abreviatura'),
                'metrica': request.POST.get('metrica'),
                'tipo': request.POST.get('tipo'),
                'valor_x_hora': request.POST.get('valor_x_hora')
            }
            
            response = requests.post(f'{settings.BACKEND_URL}/crearRecurso', json=data)
            return JsonResponse(response.json())
        except Exception as e:
            return JsonResponse({
                'mensaje': f'Error al crear recurso: {str(e)}',
                'status': 500
            })
    
    return render(request, 'crear_recurso.html')

# Similar para crear_categoria, crear_configuracion, crear_cliente, crear_instancia

def generar_factura(request):
    if request.method == 'POST':
        try:
            data = {
                'fecha_inicio': request.POST.get('fecha_inicio'),
                'fecha_fin': request.POST.get('fecha_fin')
            }
            
            response = requests.post(f'{settings.BACKEND_URL}/generarFactura', json=data)
            return JsonResponse(response.json())
        except Exception as e:
            return JsonResponse({
                'mensaje': f'Error al generar factura: {str(e)}',
                'status': 500
            })
    
    return render(request, 'generar_factura.html')

def info_estudiante(request):
    try:
        response = requests.get(f'{settings.BACKEND_URL}/infoEstudiante')
        return JsonResponse(response.json())
    except Exception as e:
        return JsonResponse({
            'nombre': 'Estudiante',
            'carnet': '00000000',
            'curso': 'IPC2'
        })

def ayuda(request):
    return render(request, 'ayuda.html')
