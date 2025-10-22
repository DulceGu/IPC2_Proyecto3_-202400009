from flask import Flask, request, jsonify
from flask_cors import CORS
import xml.etree.ElementTree as ET
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

app = Flask(__name__)
CORS(app)
db = XMLDatabase()

# Endpoint para resetear datos
@app.route('/reset', methods=['POST'])
def resetear_datos():
    try:
        lista_recursos.clear()
        lista_categorias.clear()
        lista_clientes.clear()
        lista_consumos.clear()
        lista_facturas.clear()
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
            tree = ET.parse(file)
            root = tree.getroot()
            
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
                    id_recurso = recurso_elem.get('id')
                    nombre = recurso_elem.find('nombre').text.strip()
                    abreviatura = recurso_elem.find('abreviatura').text.strip()
                    metrica = recurso_elem.find('metrica').text.strip()
                    tipo = recurso_elem.find('tipo').text.strip()
                    valor_x_hora = recurso_elem.find('valorXhora').text.strip()
                    
                    recurso = Recurso(id_recurso, nombre, abreviatura, metrica, tipo, valor_x_hora)
                    lista_recursos.append(recurso)
                    contadores['recursos'] += 1
            
            # Procesar categorías y configuraciones
            lista_categorias_elem = root.find('listaCategorias')
            if lista_categorias_elem is not None:
                for categoria_elem in lista_categorias_elem.findall('categoria'):
                    id_categoria = categoria_elem.get('id')
                    nombre = categoria_elem.find('nombre').text.strip()
                    descripcion = categoria_elem.find('descripcion').text.strip()
                    carga_trabajo = categoria_elem.find('cargaTrabajo').text.strip()
                    
                    categoria = Categoria(id_categoria, nombre, descripcion, carga_trabajo)
                    
                    # Procesar configuraciones de la categoría
                    lista_configuraciones_elem = categoria_elem.find('listaConfiguraciones')
                    if lista_configuraciones_elem is not None:
                        for config_elem in lista_configuraciones_elem.findall('configuracion'):
                            id_config = config_elem.get('id')
                            nombre_config = config_elem.find('nombre').text.strip()
                            descripcion_config = config_elem.find('descripcion').text.strip()
                            
                            configuracion = Configuracion(id_config, nombre_config, descripcion_config)
                            
                            # Procesar recursos de la configuración
                            recursos_config_elem = config_elem.find('recursosConfiguracion')
                            if recursos_config_elem is not None:
                                for recurso_config_elem in recursos_config_elem.findall('recurso'):
                                    id_recurso_config = recurso_config_elem.get('id')
                                    cantidad = recurso_config_elem.text.strip()
                                    configuracion.agregar_recurso(id_recurso_config, cantidad)
                            
                            categoria.agregar_configuracion(configuracion)
                            contadores['configuraciones'] += 1
                    
                    lista_categorias.append(categoria)
                    contadores['categorias'] += 1
            
            # Procesar clientes e instancias
            lista_clientes_elem = root.find('listaClientes')
            if lista_clientes_elem is not None:
                for cliente_elem in lista_clientes_elem.findall('cliente'):
                    nit = cliente_elem.get('nit')
                    nombre_cliente = cliente_elem.find('nombre').text.strip()
                    usuario = cliente_elem.find('usuario').text.strip()
                    clave = cliente_elem.find('clave').text.strip()
                    direccion = cliente_elem.find('direccion').text.strip()
                    correo = cliente_elem.find('correoElectronico').text.strip()
                    
                    if not validar_nit(nit):
                        continue  # Saltar cliente con NIT inválido
                    
                    cliente = Cliente(nit, nombre_cliente, usuario, clave, direccion, correo)
                    
                    # Procesar instancias del cliente
                    lista_instancias_elem = cliente_elem.find('listaInstancias')
                    if lista_instancias_elem is not None:
                        for instancia_elem in lista_instancias_elem.findall('instancia'):
                            id_instancia = instancia_elem.get('id')
                            id_configuracion = instancia_elem.find('idConfiguracion').text.strip()
                            nombre_instancia = instancia_elem.find('nombre').text.strip()
                            fecha_inicio = instancia_elem.find('fechaInicio').text.strip()
                            estado = instancia_elem.find('estado').text.strip()
                            fecha_final_elem = instancia_elem.find('fechaFinal')
                            fecha_final = fecha_final_elem.text.strip() if fecha_final_elem is not None else None
                            
                            if not validar_fecha(fecha_inicio):
                                continue  # Saltar instancia con fecha inválida
                            
                            instancia = Instancia(id_instancia, id_configuracion, nombre_instancia, fecha_inicio, estado, fecha_final)
                            cliente.agregar_instancia(instancia)
                            contadores['instancias'] += 1
                    
                    lista_clientes.append(cliente)
                    contadores['clientes'] += 1
            
            db.guardar_datos()
            
            return jsonify({
                'mensaje': 'Configuración cargada exitosamente',
                'resultados': contadores,
                'status': 200
            }), 200
        
        return jsonify({'mensaje': 'Archivo no válido', 'status': 400}), 400
    
    except Exception as e:
        return jsonify({
            'mensaje': f'Error al procesar configuración: {str(e)}',
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
            tree = ET.parse(file)
            root = tree.getroot()
            
            consumos_procesados = 0
            
            for consumo_elem in root.findall('consumo'):
                nit_cliente = consumo_elem.get('nitCliente')
                id_instancia = consumo_elem.get('idInstancia')
                tiempo = consumo_elem.find('tiempo').text.strip()
                fecha_hora = consumo_elem.find('fechahora').text.strip()
                
                if not validar_nit(nit_cliente) or not validar_fecha_hora(fecha_hora):
                    continue  # Saltar consumo con datos inválidos
                
                consumo = Consumo(nit_cliente, id_instancia, tiempo, fecha_hora)
                lista_consumos.append(consumo)
                consumos_procesados += 1
            
            db.guardar_datos()
            
            return jsonify({
                'mensaje': 'Consumos cargados exitosamente',
                'consumos_procesados': consumos_procesados,
                'status': 200
            }), 200
        
        return jsonify({'mensaje': 'Archivo no válido', 'status': 400}), 400
    
    except Exception as e:
        return jsonify({
            'mensaje': f'Error al procesar consumos: {str(e)}',
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
        data = request.json
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
        data = request.json
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
        data = request.json
        configuracion = Configuracion(
            data['id'],
            data['nombre'],
            data['descripcion']
        )
        
        # Agregar recursos a la configuración
        for recurso_data in data['recursos']:
            configuracion.agregar_recurso(recurso_data['id'], recurso_data['cantidad'])
        
        # Buscar la categoría y agregar la configuración
        id_categoria = data['id_categoria']
        for categoria in lista_categorias:
            if categoria.id == id_categoria:
                categoria.agregar_configuracion(configuracion)
                break
        
        db.guardar_datos()
        
        return jsonify({
            'mensaje': 'Configuración creada exitosamente',
            'status': 200
        }), 200
    
    except Exception as e:
        return jsonify({
            'mensaje': f'Error al crear configuración: {str(e)}',
            'status': 500
        }), 500

@app.route('/crearCliente', methods=['POST'])
def crear_cliente():
    try:
        data = request.json
        
        if not validar_nit(data['nit']):
            return jsonify({
                'mensaje': 'NIT no válido',
                'status': 400
            }), 400
        
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
        
        return jsonify({
            'mensaje': 'Cliente creado exitosamente',
            'status': 200
        }), 200
    
    except Exception as e:
        return jsonify({
            'mensaje': f'Error al crear cliente: {str(e)}',
            'status': 500
        }), 500

@app.route('/crearInstancia', methods=['POST'])
def crear_instancia():
    try:
        data = request.json
        
        if not validar_fecha(data['fecha_inicio']):
            return jsonify({
                'mensaje': 'Fecha de inicio no válida',
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
        for cliente in lista_clientes:
            if cliente.nit == nit_cliente:
                cliente.agregar_instancia(instancia)
                break
        
        db.guardar_datos()
        
        return jsonify({
            'mensaje': 'Instancia creada exitosamente',
            'status': 200
        }), 200
    
    except Exception as e:
        return jsonify({
            'mensaje': f'Error al crear instancia: {str(e)}',
            'status': 500
        }), 500

# Endpoint para generar factura
@app.route('/generarFactura', methods=['POST'])
def generar_factura():
    try:
        data = request.json
        fecha_inicio = data['fecha_inicio']
        fecha_fin = data['fecha_fin']
        
        # Lógica para generar facturas basada en consumos no facturados
        # en el rango de fechas especificado
        
        facturas_generadas = []
        
        # Implementar lógica de facturación aquí
        # Calcular consumos por cliente y generar facturas
        
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

# Endpoint de información del estudiante
@app.route('/infoEstudiante', methods=['GET'])
def info_estudiante():
    info = {
        'nombre': 'Tu Nombre',
        'carnet': 'Tu Carnet',
        'curso': 'IPC2'
    }
    return jsonify(info), 200

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
            'GET /infoEstudiante - Información del estudiante'
        ],
        'status': 200
    }), 200

if __name__ == "__main__":
    # Cargar datos existentes al iniciar
    db.cargar_datos()
    app.run(host="0.0.0.0", port=4000, debug=True)