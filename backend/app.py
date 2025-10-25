import json
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import xml.etree.ElementTree as ET
import os
from datetime import datetime
from estructuras.estructuras import *
from clases.recurso import Recurso
from clases.categoria import Categoria
from clases.configuracion import Configuracion
from clases.cliente import Cliente
from clases.instancia import Instancia
from clases.consumo import Consumo
from clases.factura import Factura
from utils.validators import validar_nit, validar_fecha, validar_fecha_hora
from database.xml_database import XMLDatabase
from utils.pdf_generator import PDFGenerator

app = Flask(__name__)
CORS(app)
db = XMLDatabase()

# Endpoint raíz
@app.route('/', methods=['GET'])
def inicio():
    return jsonify({
        'mensaje': 'API de Tecnologías Chapinas, S.A.',
        'servicio': 'Backend - Servicio 2',
        'endpoints_disponibles': [
            'POST /reset - Resetear datos',
            'POST /cargarConfiguracion - Cargar configuración desde XML',
            'POST /cargarConsumos - Cargar consumos desde XML',
            'GET /consultarDatos - Consultar todos los datos',
            'POST /crearRecurso - Crear recurso individual',
            'POST /crearCategoria - Crear categoría individual',
            'POST /crearConfiguracion - Crear configuración individual',
            'POST /crearCliente - Crear cliente individual',
            'POST /crearInstancia - Crear instancia individual',
            'POST /generarFactura - Generar facturas',
            'GET /infoEstudiante - Información del estudiante',
            'POST /generarPDF - Generar reportes PDF'
        ],
        'status': 200
    }), 200

# Endpoint para resetear datos
@app.route('/reset', methods=['POST'])
def resetear_datos():
    try:
        lista_recursos.clear()
        lista_categorias.clear()
        lista_clientes.clear()
        lista_consumos.clear()
        lista_facturas.clear()
        global contador_facturas
        contador_facturas = 1
        
        db.guardar_datos()
        
        return jsonify({
            'mensaje': 'Datos reseteados exitosamente',
            'status': 200
        }), 200
    except Exception as e:
        return jsonify({
            'mensaje': f'Error al resetear datos: {str(e)}',
            'status': 500
        }), 500

# Endpoint para cargar configuración desde XML
@app.route('/cargarConfiguracion', methods=['POST'])
def cargar_configuracion():
    try:
        if 'file' not in request.files:
            return jsonify({'mensaje': 'No se envió archivo', 'status': 400}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'mensaje': 'No se seleccionó archivo', 'status': 400}), 400
        
        if file and file.filename.endswith('.xml'):
            # Limpiar datos existentes
            lista_recursos.clear()
            lista_categorias.clear()
            lista_clientes.clear()
            
            # Leer el contenido del archivo
            file_content = file.read().decode('utf-8')
            print("=== CONTENIDO DEL ARCHIVO ===")
            print(file_content[:500] + "..." if len(file_content) > 500 else file_content)
            print("==============================")
            
            # Parsear XML
            try:
                root = ET.fromstring(file_content)
            except ET.ParseError as e:
                return jsonify({
                    'mensaje': f'Error al parsear XML: {str(e)}',
                    'status': 400
                }), 400
            
            contadores = {
                'recursos': 0,
                'categorias': 0,
                'configuraciones': 0,
                'clientes': 0,
                'instancias': 0
            }
            
            # Procesar recursos
            lista_recursos_elem = root.find('listaRecursos')
            if lista_recursos_elem is not None:
                for recurso_elem in lista_recursos_elem.findall('recurso'):
                    try:
                        id_recurso = recurso_elem.get('id')
                        nombre = recurso_elem.find('nombre').text.strip() if recurso_elem.find('nombre') is not None else ''
                        abreviatura = recurso_elem.find('abreviatura').text.strip() if recurso_elem.find('abreviatura') is not None else ''
                        metrica = recurso_elem.find('metrica').text.strip() if recurso_elem.find('metrica') is not None else ''
                        tipo = recurso_elem.find('tipo').text.strip() if recurso_elem.find('tipo') is not None else ''
                        valor_x_hora = recurso_elem.find('valorXhora').text.strip() if recurso_elem.find('valorXhora') is not None else '0'
                        
                        if not all([id_recurso, nombre, abreviatura, metrica, tipo, valor_x_hora]):
                            print(f"Recurso incompleto: {id_recurso}")
                            continue
                            
                        recurso = Recurso(id_recurso, nombre, abreviatura, metrica, tipo, valor_x_hora)
                        lista_recursos.append(recurso)
                        contadores['recursos'] += 1
                        print(f"Recurso agregado: {nombre}")
                    except Exception as e:
                        print(f"Error procesando recurso: {e}")
                        continue
            
            # Procesar categorías y configuraciones
            lista_categorias_elem = root.find('listaCategorias')
            if lista_categorias_elem is not None:
                for categoria_elem in lista_categorias_elem.findall('categoria'):
                    try:
                        id_categoria = categoria_elem.get('id')
                        nombre = categoria_elem.find('nombre').text.strip() if categoria_elem.find('nombre') is not None else ''
                        
                        # Buscar descripción con diferentes nombres posibles
                        descripcion_elem = categoria_elem.find('descripcion')
                        if descripcion_elem is None:
                            descripcion_elem = categoria_elem.find('description')  # Intentar con nombre en inglés
                        descripcion = descripcion_elem.text.strip() if descripcion_elem is not None and descripcion_elem.text else ''
                        
                        carga_trabajo = categoria_elem.find('cargaTrabajo').text.strip() if categoria_elem.find('cargaTrabajo') is not None else ''
                        
                        if not all([id_categoria, nombre, descripcion, carga_trabajo]):
                            print(f"Categoría incompleta: {id_categoria}")
                            continue
                            
                        categoria = Categoria(id_categoria, nombre, descripcion, carga_trabajo)
                        
                        # Procesar configuraciones de la categoría
                        lista_configuraciones_elem = categoria_elem.find('listaConfiguraciones')
                        if lista_configuraciones_elem is not None:
                            for config_elem in lista_configuraciones_elem.findall('configuracion'):
                                try:
                                    id_config = config_elem.get('id')
                                    nombre_config = config_elem.find('nombre').text.strip() if config_elem.find('nombre') is not None else ''
                                    
                                    # Buscar descripción con diferentes nombres posibles
                                    descripcion_config_elem = config_elem.find('descripcion')
                                    if descripcion_config_elem is None:
                                        descripcion_config_elem = config_elem.find('description')  # Intentar con nombre en inglés
                                    descripcion_config = descripcion_config_elem.text.strip() if descripcion_config_elem is not None and descripcion_config_elem.text else ''
                                    
                                    if not all([id_config, nombre_config, descripcion_config]):
                                        print(f"Configuración incompleta: {id_config}")
                                        continue
                                        
                                    configuracion = Configuracion(id_config, nombre_config, descripcion_config)
                                    
                                    # Procesar recursos de la configuración
                                    recursos_config_elem = config_elem.find('recursosConfiguracion')
                                    if recursos_config_elem is not None:
                                        for recurso_config_elem in recursos_config_elem.findall('recurso'):
                                            try:
                                                id_recurso_config = recurso_config_elem.get('id')
                                                cantidad = recurso_config_elem.text.strip() if recurso_config_elem.text else '0'
                                                
                                                if id_recurso_config and cantidad:
                                                    configuracion.agregar_recurso(id_recurso_config, cantidad)
                                                    print(f"Recurso {id_recurso_config} agregado a configuración {id_config}")
                                            except Exception as e:
                                                print(f"Error procesando recurso de configuración: {e}")
                                                continue
                                    
                                    categoria.agregar_configuracion(configuracion)
                                    contadores['configuraciones'] += 1
                                    print(f"Configuración agregada: {nombre_config}")
                                except Exception as e:
                                    print(f"Error procesando configuración: {e}")
                                    continue
                    
                        lista_categorias.append(categoria)
                        contadores['categorias'] += 1
                        print(f"Categoría agregada: {nombre}")
                    except Exception as e:
                        print(f"Error procesando categoría: {e}")
                        continue
            
            # Procesar clientes e instancias
            lista_clientes_elem = root.find('listaClientes')
            if lista_clientes_elem is not None:
                for cliente_elem in lista_clientes_elem.findall('cliente'):
                    try:
                        nit = cliente_elem.get('nit')
                        nombre_cliente = cliente_elem.find('nombre').text.strip() if cliente_elem.find('nombre') is not None else ''
                        usuario = cliente_elem.find('usuario').text.strip() if cliente_elem.find('usuario') is not None else ''
                        clave = cliente_elem.find('clave').text.strip() if cliente_elem.find('clave') is not None else ''
                        direccion = cliente_elem.find('direccion').text.strip() if cliente_elem.find('direccion') is not None else ''
                        correo = cliente_elem.find('correoElectronico').text.strip() if cliente_elem.find('correoElectronico') is not None else ''
                        
                        if not all([nit, nombre_cliente, usuario, clave, direccion, correo]):
                            print(f"Cliente incompleto: {nit}")
                            continue
                            
                        if not validar_nit(nit):
                            print(f"NIT inválido: {nit}")
                            continue
                        
                        cliente = Cliente(nit, nombre_cliente, usuario, clave, direccion, correo)
                        
                        # Procesar instancias del cliente
                        lista_instancias_elem = cliente_elem.find('listaInstancias')
                        if lista_instancias_elem is not None:
                            for instancia_elem in lista_instancias_elem.findall('instancia'):
                                try:
                                    id_instancia = instancia_elem.get('id')
                                    id_configuracion = instancia_elem.find('idConfiguracion').text.strip() if instancia_elem.find('idConfiguracion') is not None else ''
                                    nombre_instancia = instancia_elem.find('nombre').text.strip() if instancia_elem.find('nombre') is not None else ''
                                    fecha_inicio = instancia_elem.find('fechaInicio').text.strip() if instancia_elem.find('fechaInicio') is not None else ''
                                    estado = instancia_elem.find('estado').text.strip() if instancia_elem.find('estado') is not None else 'Vigente'
                                    
                                    fecha_final_elem = instancia_elem.find('fechaFinal')
                                    fecha_final = None
                                    if fecha_final_elem is not None and fecha_final_elem.text and fecha_final_elem.text.strip():
                                        fecha_final = fecha_final_elem.text.strip()
                                    
                                    if not all([id_instancia, id_configuracion, nombre_instancia, fecha_inicio]):
                                        print(f"Instancia incompleta: {id_instancia}")
                                        continue
                                        
                                    if not validar_fecha(fecha_inicio):
                                        print(f"Fecha de inicio inválida: {fecha_inicio}")
                                        continue
                                    
                                    instancia = Instancia(id_instancia, id_configuracion, nombre_instancia, fecha_inicio, estado, fecha_final)
                                    cliente.agregar_instancia(instancia)
                                    contadores['instancias'] += 1
                                    print(f"Instancia agregada: {nombre_instancia}")
                                except Exception as e:
                                    print(f"Error procesando instancia: {e}")
                                    continue
                    
                        lista_clientes.append(cliente)
                        contadores['clientes'] += 1
                        print(f"Cliente agregado: {nombre_cliente}")
                    except Exception as e:
                        print(f"Error procesando cliente: {e}")
                        continue
            
            db.guardar_datos()
            
            print("=== RESUMEN FINAL ===")
            print(f"Recursos: {contadores['recursos']}")
            print(f"Categorías: {contadores['categorias']}")
            print(f"Configuraciones: {contadores['configuraciones']}")
            print(f"Clientes: {contadores['clientes']}")
            print(f"Instancias: {contadores['instancias']}")
            print("=====================")
            
            return jsonify({
                'mensaje': 'Configuración cargada exitosamente',
                'resultados': contadores,
                'status': 200
            }), 200
        
        return jsonify({'mensaje': 'Archivo no válido', 'status': 400}), 400
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print("=== ERROR DETALLADO ===")
        print(error_details)
        print("=======================")
        
        return jsonify({
            'mensaje': f'Error al procesar configuración: {str(e)}',
            'detalles': error_details,
            'status': 500
        }), 500

# Endpoint para cargar consumos desde XML
@app.route('/cargarConsumos', methods=['POST'])
def cargar_consumos():
    try:
        if 'file' not in request.files:
            return jsonify({'mensaje': 'No se envió archivo', 'status': 400}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'mensaje': 'No se seleccionó archivo', 'status': 400}), 400
        
        if file and file.filename.endswith('.xml'):
            # Leer el contenido del archivo
            file_content = file.read().decode('utf-8')
            print("=== CONTENIDO DEL ARCHIVO CONSUMOS ===")
            print(file_content)
            print("======================================")
            
            try:
                root = ET.fromstring(file_content)
            except ET.ParseError as e:
                return jsonify({
                    'mensaje': f'Error al parsear XML: {str(e)}',
                    'status': 400
                }), 400
            
            consumos_procesados = 0
            
            for consumo_elem in root.findall('consumo'):
                try:
                    nit_cliente = consumo_elem.get('nitCliente')
                    id_instancia = consumo_elem.get('idInstancia')
                    
                    tiempo_elem = consumo_elem.find('tiempo')
                    tiempo = tiempo_elem.text.strip() if tiempo_elem is not None and tiempo_elem.text else '0'
                    
                    fecha_hora_elem = consumo_elem.find('fechahora')
                    fecha_hora = fecha_hora_elem.text.strip() if fecha_hora_elem is not None and fecha_hora_elem.text else ''
                    
                    if not all([nit_cliente, id_instancia, tiempo, fecha_hora]):
                        print(f"Consumo incompleto: {nit_cliente} - {id_instancia}")
                        continue
                    
                    if not validar_nit(nit_cliente):
                        print(f"NIT inválido en consumo: {nit_cliente}")
                        continue
                        
                    if not validar_fecha_hora(fecha_hora):
                        print(f"Fecha/hora inválida en consumo: {fecha_hora}")
                        continue
                    
                    consumo = Consumo(nit_cliente, id_instancia, tiempo, fecha_hora)
                    lista_consumos.append(consumo)
                    consumos_procesados += 1
                    print(f"Consumo agregado: {nit_cliente} - Instancia {id_instancia} - {tiempo} horas")
                except Exception as e:
                    print(f"Error procesando consumo: {e}")
                    continue
            
            db.guardar_datos()
            
            return jsonify({
                'mensaje': 'Consumos cargados exitosamente',
                'consumos_procesados': consumos_procesados,
                'status': 200
            }), 200
        
        return jsonify({'mensaje': 'Archivo no válido', 'status': 400}), 400
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print("=== ERROR DETALLADO CONSUMOS ===")
        print(error_details)
        print("================================")
        
        return jsonify({
            'mensaje': f'Error al procesar consumos: {str(e)}',
            'detalles': error_details,
            'status': 500
        }), 500

# Endpoint para consultar datos
@app.route('/consultarDatos', methods=['GET'])
def consultar_datos():
    try:
        tipo = request.args.get('tipo', 'todos')
        
        datos = {}
        
        if tipo in ['todos', 'recursos']:
            datos['recursos'] = [recurso.to_dict() for recurso in lista_recursos]
        
        if tipo in ['todos', 'categorias']:
            datos['categorias'] = [categoria.to_dict() for categoria in lista_categorias]
        
        if tipo in ['todos', 'clientes']:
            datos['clientes'] = [cliente.to_dict() for cliente in lista_clientes]
        
        if tipo in ['todos', 'consumos']:
            datos['consumos'] = [consumo.to_dict() for consumo in lista_consumos]
        
        if tipo in ['todos', 'facturas']:
            datos['facturas'] = [factura.to_dict() for factura in lista_facturas]
        
        return jsonify({
            'datos': datos,
            'status': 200
        }), 200
    
    except Exception as e:
        return jsonify({
            'mensaje': f'Error al consultar datos: {str(e)}',
            'status': 500
        }), 500

# Endpoints para crear recursos individualmente
@app.route('/crearRecurso', methods=['POST'])
def crear_recurso():
    try:
        data = request.get_json()
        # Verificar si el recurso ya existe
        for recurso in lista_recursos:
            if recurso.id == data['id']:
                return jsonify({
                    'mensaje': 'Ya existe un recurso con ese ID',
                    'status': 400
                }), 400
        
        recurso = Recurso(
            data['id'],
            data['nombre'],
            data['abreviatura'],
            data['metrica'],
            data['tipo'],
            data['valor_x_hora']
        )
        lista_recursos.append(recurso)
        db.guardar_datos()
        
        return jsonify({
            'mensaje': 'Recurso creado exitosamente',
            'status': 200
        }), 200
    
    except Exception as e:
        return jsonify({
            'mensaje': f'Error al crear recurso: {str(e)}',
            'status': 500
        }), 500

@app.route('/crearCategoria', methods=['POST'])
def crear_categoria():
    try:
        data = request.get_json()
        # Verificar si la categoría ya existe
        for categoria in lista_categorias:
            if categoria.id == data['id']:
                return jsonify({
                    'mensaje': 'Ya existe una categoría con ese ID',
                    'status': 400
                }), 400
        
        categoria = Categoria(
            data['id'],
            data['nombre'],
            data['descripcion'],
            data['carga_trabajo']
        )
        lista_categorias.append(categoria)
        db.guardar_datos()
        
        return jsonify({
            'mensaje': 'Categoría creada exitosamente',
            'status': 200
        }), 200
    
    except Exception as e:
        return jsonify({
            'mensaje': f'Error al crear categoría: {str(e)}',
            'status': 500
        }), 500

@app.route('/crearConfiguracion', methods=['POST'])
def crear_configuracion():
    try:
        print("🎯 === SOLICITUD RECIBIDA EN /crearConfiguracion ===")
        
        # Debug: mostrar headers
        print("📨 Headers:", dict(request.headers))
        
        # Debug: mostrar datos crudos
        raw_data = request.get_data(as_text=True)
        print("📦 Datos crudos recibidos:", raw_data)
        print("🔍 Tipo de datos crudos:", type(raw_data))
        
        # Intentar parsear JSON de múltiples maneras
        data = None
        
        # Método 1: request.get_json()
        try:
            data = request.get_json()
            print("✅ Datos parseados con get_json():", data)
        except Exception as e:
            print("❌ Error con get_json():", e)
        
        # Método 2: json.loads manual
        if data is None:
            try:
                import json
                data = json.loads(raw_data)
                print(" Datos parseados con json.loads():", data)
            except Exception as e:
                print(" Error con json.loads():", e)
        
        # Método 3: Si todo falla, crear datos de prueba
        if data is None:
            print(" Usando datos de prueba")
            data = {
                'id': 'test-from-backend',
                'nombre': 'Test Backend',
                'descripcion': 'Prueba desde backend',
                'id_categoria': '1',
                'recursos': [{'id': '1', 'cantidad': '2'}]
            }
        
        print(" Datos finales a procesar:", data)
        print(" Tipo de datos final:", type(data))
        
        # Validar datos requeridos
        if not data.get('id') or not data.get('nombre') or not data.get('id_categoria'):
            error_msg = f" Faltan datos: id={data.get('id')}, nombre={data.get('nombre')}, id_categoria={data.get('id_categoria')}"
            print(error_msg)
            return jsonify({
                'mensaje': error_msg,
                'status': 400
            }), 400
        
        # Verificar si la configuración ya existe
        config_existente = False
        for categoria in lista_categorias:
            for config in categoria.configuraciones:
                if config.id == data['id']:
                    config_existente = True
                    break
            if config_existente:
                break
        
        if config_existente:
            return jsonify({
                'mensaje': 'Ya existe una configuración con ese ID',
                'status': 400
            }), 400
        
        # Crear la configuración
        configuracion = Configuracion(
            data['id'],
            data['nombre'],
            data.get('descripcion', '')
        )
        
        # Agregar recursos a la configuración
        recursos_data = data.get('recursos', [])
        print(f" Agregando {len(recursos_data)} recursos a la configuración")
        
        for recurso_data in recursos_data:
            recurso_id = recurso_data.get('id')
            cantidad = recurso_data.get('cantidad')
            print(f" Agregando recurso {recurso_id} con cantidad {cantidad}")
            
            if recurso_id and cantidad:
                configuracion.agregar_recurso(recurso_id, cantidad)
        
        # Buscar la categoría y agregar la configuración
        id_categoria = data['id_categoria']
        categoria_encontrada = None
        
        print(f" Buscando categoría con ID: {id_categoria}")
        print(" Categorías disponibles:", [cat.id for cat in lista_categorias])
        
        for categoria in lista_categorias:
            print(f" Comparando: '{categoria.id}' == '{id_categoria}' -> {categoria.id == id_categoria}")
            if categoria.id == id_categoria:
                categoria_encontrada = categoria
                break
        
        if categoria_encontrada:
            categoria_encontrada.agregar_configuracion(configuracion)
            print(f"Configuración '{configuracion.nombre}' agregada a categoría '{categoria_encontrada.nombre}'")
            print(f" Recursos en configuración: {configuracion.recursos}")
            
            db.guardar_datos()
            
            return jsonify({
                'mensaje': 'Configuración creada exitosamente',
                'configuracion': configuracion.to_dict(),
                'status': 200
            }), 200
        else:
            print(f" No se encontró categoría con ID: {id_categoria}")
            return jsonify({
                'mensaje': f'No se encontró la categoría especificada (ID: {id_categoria})',
                'status': 404
            }), 404
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(" === ERROR CRÍTICO ===")
        print(error_details)
        print("=======================")
        
        return jsonify({
            'mensaje': f'Error al crear configuración: {str(e)}',
            'detalles': error_details,
            'status': 500
        }), 500
    
@app.route('/test-json', methods=['POST'])
def test_json():
    """Endpoint para probar recepción de JSON"""
    print(" === TEST JSON ENDPOINT ===")
    print("Headers:", dict(request.headers))
    print("Content-Type:", request.content_type)
    
    # Intentar diferentes métodos de parseo
    data1 = request.get_json()
    data2 = request.json
    raw_data = request.get_data(as_text=True)
    
    print("request.get_json():", data1)
    print("request.json:", data2) 
    print("request.get_data():", raw_data)
    
    try:
        import json
        data3 = json.loads(raw_data)
        print("json.loads():", data3)
    except Exception as e:
        print("Error json.loads():", e)
    
    return jsonify({
        'received_get_json': data1,
        'received_json': data2,
        'received_raw': raw_data,
        'status': 200
    }), 200

@app.route('/crearCliente', methods=['POST'])
def crear_cliente():
    try:
        print("🎯 === SOLICITUD RECIBIDA EN /crearCliente ===")
        print("📨 Headers:", dict(request.headers))
        print("🔍 Content-Type:", request.content_type)
        
        # Debug: mostrar datos crudos
        raw_data = request.get_data(as_text=True)
        print("📦 Datos crudos recibidos:", raw_data)
        
        data = request.get_json()
        print("✅ Datos parseados:", data)
        
        if not data:
            return jsonify({
                'mensaje': 'No se recibieron datos JSON',
                'status': 400
            }), 400
        
        # Validar NIT
        if not validar_nit(data['nit']):
            return jsonify({
                'mensaje': 'NIT no válido',
                'status': 400
            }), 400
        
        # Verificar si el cliente ya existe
        for cliente in lista_clientes:
            if cliente.nit == data['nit']:
                return jsonify({
                    'mensaje': 'Ya existe un cliente con ese NIT',
                    'status': 400
                }), 400
        
        # Crear cliente
        cliente = Cliente(
            data['nit'],
            data['nombre'],
            data['usuario'],
            data['clave'],
            data['direccion'],
            data['correo_electronico']
        )
        lista_clientes.append(cliente)
        db.guardar_datos()
        
        print(f"✅ Cliente creado exitosamente: {data['nombre']} (NIT: {data['nit']})")
        
        return jsonify({
            'mensaje': 'Cliente creado exitosamente',
            'status': 200
        }), 200
    
    except Exception as e:
        print(f"💥 Error al crear cliente: {str(e)}")
        import traceback
        print("📋 Traceback:", traceback.format_exc())
        
        return jsonify({
            'mensaje': f'Error al crear cliente: {str(e)}',
            'status': 500
        }), 500
    
@app.route('/crearInstancia', methods=['POST'])
def crear_instancia():
    try:
        data = request.get_json()
        
        if not validar_fecha(data['fecha_inicio']):
            return jsonify({
                'mensaje': 'Fecha de inicio no válida',
                'status': 400
            }), 400
        
        # Verificar si la instancia ya existe
        for cliente in lista_clientes:
            for instancia in cliente.instancias:
                if instancia.id == data['id']:
                    return jsonify({
                        'mensaje': 'Ya existe una instancia con ese ID',
                        'status': 400
                    }), 400
        
        instancia = Instancia(
            data['id'],
            data['id_configuracion'],
            data['nombre'],
            data['fecha_inicio'],
            data.get('estado', 'Vigente'),
            data.get('fecha_final')
        )
        
        # Buscar el cliente y agregar la instancia
        nit_cliente = data['nit_cliente']
        cliente_encontrado = None
        for cliente in lista_clientes:
            if cliente.nit == nit_cliente:
                cliente_encontrado = cliente
                break
        
        if cliente_encontrado:
            cliente_encontrado.agregar_instancia(instancia)
            db.guardar_datos()
            
            return jsonify({
                'mensaje': 'Instancia creada exitosamente',
                'status': 200
            }), 200
        else:
            return jsonify({
                'mensaje': 'No se encontró el cliente especificado',
                'status': 404
            }), 404
    
    except Exception as e:
        return jsonify({
            'mensaje': f'Error al crear instancia: {str(e)}',
            'status': 500
        }), 500

# Endpoint para generar factura
@app.route('/generarFactura', methods=['POST'])
def generar_factura():
    try:
        data = request.get_json()
        fecha_inicio = data['fecha_inicio']
        fecha_fin = data['fecha_fin']
        
        facturas_generadas = []
        
        # Procesar cada cliente
        for cliente in lista_clientes:
            # Filtrar consumos del cliente en el rango de fechas
            consumos_cliente = []
            for consumo in lista_consumos:
                if (consumo.nit_cliente == cliente.nit and 
                    consumo.fecha_hora and 
                    fecha_inicio <= consumo.fecha_hora.strftime('%Y-%m-%d') <= fecha_fin):
                    consumos_cliente.append(consumo)
            
            if not consumos_cliente:
                continue
            
            # Crear factura para el cliente
            global contador_facturas
            factura_numero = f"F-{contador_facturas:06d}"
            contador_facturas += 1
            
            factura = Factura(factura_numero, cliente.nit, fecha_fin)
            
            # Procesar cada consumo
            for consumo in consumos_cliente:
                # Buscar la instancia
                instancia = None
                for cli in lista_clientes:
                    for inst in cli.instancias:
                        if inst.id == consumo.id_instancia:
                            instancia = inst
                            break
                    if instancia:
                        break
                
                if not instancia:
                    continue
                
                # Buscar la configuración de la instancia
                configuracion = None
                for categoria in lista_categorias:
                    for config in categoria.configuraciones:
                        if config.id == instancia.id_configuracion:
                            configuracion = config
                            break
                    if configuracion:
                        break
                
                if not configuracion:
                    continue
                
                # Calcular costos por recurso
                for recurso_id, cantidad in configuracion.recursos.items():
                    # Buscar el recurso
                    recurso = next((r for r in lista_recursos if r.id == recurso_id), None)
                    if recurso:
                        subtotal = float(cantidad) * consumo.tiempo * recurso.valor_x_hora
                        
                        detalle = {
                            'id_instancia': instancia.id,
                            'nombre_instancia': instancia.nombre,
                            'id_recurso': recurso.id,
                            'nombre_recurso': recurso.nombre,
                            'cantidad': cantidad,
                            'tiempo': consumo.tiempo,
                            'valor_x_hora': recurso.valor_x_hora,
                            'subtotal': subtotal
                        }
                        factura.agregar_detalle(detalle)
            
            if factura.detalles:
                lista_facturas.append(factura)
                facturas_generadas.append({
                    'numero': factura.numero,
                    'cliente': cliente.nombre,
                    'monto': factura.monto_total
                })
        
        db.guardar_datos()
        
        return jsonify({
            'mensaje': 'Facturas generadas exitosamente',
            'facturas_generadas': facturas_generadas,
            'status': 200
        }), 200
    
    except Exception as e:
        return jsonify({
            'mensaje': f'Error al generar facturas: {str(e)}',
            'status': 500
        }), 500

# Endpoint para generar PDF
@app.route('/generarPDF', methods=['POST'])
def generar_pdf():
    try:
        data = request.get_json()
        tipo = data['tipo']
        
        if tipo == 'detalle_factura':
            numero_factura = data['numero_factura']
            
            # Buscar la factura
            factura = next((f for f in lista_facturas if f.numero == numero_factura), None)
            if not factura:
                return jsonify({'mensaje': 'Factura no encontrada', 'status': 404}), 404
            
            # Buscar el cliente
            cliente = next((c for c in lista_clientes if c.nit == factura.nit_cliente), None)
            if not cliente:
                return jsonify({'mensaje': 'Cliente no encontrado', 'status': 404}), 404
            
            output_path = f"temp_detalle_factura_{numero_factura}.pdf"
            PDFGenerator.generar_detalle_factura(factura, cliente, output_path)
            
            return send_file(output_path, as_attachment=True)
        
        elif tipo == 'analisis_ventas':
            subtipo = data['subtipo']
            fecha_inicio = data['fecha_inicio']
            fecha_fin = data['fecha_fin']
            
            datos = []
            if subtipo == 'categorias':
                # Análisis por categorías y configuraciones
                for categoria in lista_categorias:
                    for configuracion in categoria.configuraciones:
                        total_config = 0
                        # Calcular ingresos de esta configuración
                        for factura in lista_facturas:
                            if fecha_inicio <= factura.fecha_factura <= fecha_fin:
                                for detalle in factura.detalles:
                                    # Aquí se necesitaría más lógica para asociar detalles con configuraciones
                                    pass
                        datos.append({
                            'categoria': categoria.nombre,
                            'configuracion': configuracion.nombre,
                            'ingresos': total_config
                        })
            
            elif subtipo == 'recursos':
                # Análisis por recursos
                for recurso in lista_recursos:
                    total_recurso = 0
                    for factura in lista_facturas:
                        if fecha_inicio <= factura.fecha_factura <= fecha_fin:
                            for detalle in factura.detalles:
                                if detalle.get('id_recurso') == recurso.id:
                                    total_recurso += detalle.get('subtotal', 0)
                    datos.append({
                        'recurso': recurso.nombre,
                        'ingresos': total_recurso
                    })
            
            output_path = f"temp_analisis_{subtipo}.pdf"
            PDFGenerator.generar_analisis_ventas(
                subtipo, 
                datos, 
                {'inicio': fecha_inicio, 'fin': fecha_fin},
                output_path
            )
            
            return send_file(output_path, as_attachment=True)
        
        return jsonify({'mensaje': 'Tipo de PDF no válido', 'status': 400}), 400
    
    except Exception as e:
        return jsonify({
            'mensaje': f'Error al generar PDF: {str(e)}',
            'status': 500
        }), 500

# Endpoint de información del estudiante
@app.route('/infoEstudiante', methods=['GET'])
def info_estudiante():
    info = {
        'nombre': 'Dulce María Rodas Martínez',
        'carnet': '202100312',
        'curso': 'IPC2 - Sección D'
    }
    return jsonify(info), 200

if __name__ == "__main__":
    # Cargar datos existentes al iniciar
    db.cargar_datos()
    app.run(host="0.0.0.0", port=4000, debug=True)