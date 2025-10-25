import requests
import json
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

def index(request):
    return render(request, 'index.html')

@csrf_exempt
def enviar_configuracion(request):
    if request.method == 'POST' and request.FILES.get('archivo_configuracion'):
        archivo = request.FILES['archivo_configuracion']
        
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

@csrf_exempt
def enviar_consumo(request):
    if request.method == 'POST' and request.FILES.get('archivo_consumo'):
        archivo = request.FILES['archivo_consumo']
        
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

@csrf_exempt
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

def crear_datos(request):
    tipo = request.GET.get('tipo', 'recurso')
    return render(request, 'crear_datos.html', {'tipo': tipo})


@csrf_exempt
def crear_recurso(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.body else {}
            print("📦 Datos recurso:", data)
            
            response = requests.post(
                f'{settings.BACKEND_URL}/crearRecurso',
                json=data
            )
            return JsonResponse(response.json())
        except Exception as e:
            return JsonResponse({
                'mensaje': f'Error al crear recurso: {str(e)}',
                'status': 500
            })
    
    return JsonResponse({'mensaje': 'Método no permitido', 'status': 405})

@csrf_exempt
def crear_categoria(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.body else {}
            print("📦 Datos categoría:", data)
            
            response = requests.post(
                f'{settings.BACKEND_URL}/crearCategoria',
                json=data
            )
            return JsonResponse(response.json())
        except Exception as e:
            return JsonResponse({
                'mensaje': f'Error al crear categoría: {str(e)}',
                'status': 500
            })
    
    return JsonResponse({'mensaje': 'Método no permitido', 'status': 405})

@csrf_exempt
def crear_configuracion(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.body else {}
            print("📦 Datos configuración:", data)
            
            response = requests.post(
                f'{settings.BACKEND_URL}/crearConfiguracion',
                json=data
            )
            return JsonResponse(response.json())
        except Exception as e:
            return JsonResponse({
                'mensaje': f'Error al crear configuración: {str(e)}',
                'status': 500
            })
    
    return JsonResponse({'mensaje': 'Método no permitido', 'status': 405})

@csrf_exempt
def crear_cliente(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.body else {}
            print("📦 Datos cliente:", data)
            
            response = requests.post(
                f'{settings.BACKEND_URL}/crearCliente',
                json=data
            )
            return JsonResponse(response.json())
        except Exception as e:
            return JsonResponse({
                'mensaje': f'Error al crear cliente: {str(e)}',
                'status': 500
            })
    
    return JsonResponse({'mensaje': 'Método no permitido', 'status': 405})

@csrf_exempt
def crear_instancia(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.body else {}
            print("📦 Datos instancia:", data)
            
            response = requests.post(
                f'{settings.BACKEND_URL}/crearInstancia',
                json=data
            )
            return JsonResponse(response.json())
        except Exception as e:
            return JsonResponse({
                'mensaje': f'Error al crear instancia: {str(e)}',
                'status': 500
            })
    
    return JsonResponse({'mensaje': 'Método no permitido', 'status': 405})

def proceso_facturacion(request):
    return render(request, 'proceso_facturacion.html')

@csrf_exempt
def generar_factura(request):
    if request.method == 'POST':
        try:
            print("🎯 === VISTA generar_factura LLAMADA ===")
            
            # Para datos JSON
            import json
            if request.body:
                data = json.loads(request.body)
                print("📨 Datos JSON recibidos:", data)
            else:
                data = {}
                print("⚠️ No se recibieron datos en el body")
            
            # Enviar al backend Flask
            backend_url = f'{settings.BACKEND_URL}/generarFactura'
            print(f"🚀 Enviando a: {backend_url}")
            
            response = requests.post(
                backend_url, 
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"📨 Respuesta del backend: {response.status_code}")
            return JsonResponse(response.json())
            
        except Exception as e:
            print(f"💥 Error en generar_factura: {e}")
            return JsonResponse({
                'mensaje': f'Error al generar factura: {str(e)}',
                'status': 500
            })
    
    return JsonResponse({'mensaje': 'Método no permitido', 'status': 405})

def reportes_pdf(request):
    return render(request, 'reportes_pdf.html')

@csrf_exempt
def generar_pdf(request):
    if request.method == 'POST':
        try:
            print("🎯 === VISTA generar_pdf LLAMADA ===")
            
            # Para datos JSON
            import json
            if request.body:
                data = json.loads(request.body)
                print("📨 Datos JSON recibidos para PDF:", data)
            else:
                data = {}
                print("⚠️ No se recibieron datos en el body para PDF")
            
            # Enviar al backend Flask
            backend_url = f'{settings.BACKEND_URL}/generarPDF'
            response = requests.post(
                backend_url, 
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"📨 Respuesta del backend PDF: {response.status_code}")
            
            if response.status_code == 200:
                # Si es un PDF, devolverlo directamente
                if 'application/pdf' in response.headers.get('content-type', ''):
                    pdf_response = HttpResponse(
                        response.content,
                        content_type='application/pdf'
                    )
                    filename = f"reporte_{data.get('tipo', 'general')}.pdf"
                    pdf_response['Content-Disposition'] = f'attachment; filename="{filename}"'
                    return pdf_response
                else:
                    # Si no es PDF, devolver como JSON
                    return JsonResponse(response.json())
            else:
                return JsonResponse(response.json())
                
        except Exception as e:
            print(f"💥 Error en generar_pdf: {e}")
            return JsonResponse({
                'mensaje': f'Error al generar PDF: {str(e)}',
                'status': 500
            })
    
    return JsonResponse({'mensaje': 'Método no permitido', 'status': 405})

def info_estudiante(request):
    try:
        response = requests.get(f'{settings.BACKEND_URL}/infoEstudiante')
        return JsonResponse(response.json())
    except Exception as e:
        return JsonResponse({
            'nombre': 'Dulce María Rodas Martínez',
            'carnet': '202100312',
            'curso': 'IPC2 - Sección D'
        })

def ayuda(request):
    return render(request, 'ayuda.html')