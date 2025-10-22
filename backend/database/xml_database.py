import xml.etree.ElementTree as ET
import os
from estructuras.estructuras import *
from clases.recurso import Recurso
from clases.categoria import Categoria
from clases.configuracion import Configuracion
from clases.cliente import Cliente
from clases.instancia import Instancia
from clases.consumo import Consumo
from clases.factura import Factura

class XMLDatabase:
    def __init__(self):
        self.data_dir = "data"
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def guardar_datos(self):
        self._guardar_recursos()
        self._guardar_categorias()
        self._guardar_clientes()
        self._guardar_consumos()
        self._guardar_facturas()
    
    def cargar_datos(self):
        try:
            self._cargar_recursos()
            self._cargar_categorias()
            self._cargar_clientes()
            self._cargar_consumos()
            self._cargar_facturas()
        except FileNotFoundError:
            print("Archivos de datos no encontrados. Se iniciará con datos vacíos.")
        except Exception as e:
            print(f"Error al cargar datos: {e}")
    
    def _guardar_recursos(self):
        root = ET.Element("listaRecursos")
        for recurso in lista_recursos:
            elem = ET.SubElement(root, "recurso")
            elem.set("id", recurso.id)
            ET.SubElement(elem, "nombre").text = recurso.nombre
            ET.SubElement(elem, "abreviatura").text = recurso.abreviatura
            ET.SubElement(elem, "metrica").text = recurso.metrica
            ET.SubElement(elem, "tipo").text = recurso.tipo
            ET.SubElement(elem, "valorXhora").text = str(recurso.valor_x_hora)
        
        tree = ET.ElementTree(root)
        tree.write(f"{self.data_dir}/recursos.xml", encoding="utf-8", xml_declaration=True)
    
    def _cargar_recursos(self):
        if not os.path.exists(f"{self.data_dir}/recursos.xml"):
            return
        
        tree = ET.parse(f"{self.data_dir}/recursos.xml")
        root = tree.getroot()
        
        for recurso_elem in root.findall('recurso'):
            id_recurso = recurso_elem.get('id')
            nombre = recurso_elem.find('nombre').text
            abreviatura = recurso_elem.find('abreviatura').text
            metrica = recurso_elem.find('metrica').text
            tipo = recurso_elem.find('tipo').text
            valor_x_hora = recurso_elem.find('valorXhora').text
            
            recurso = Recurso(id_recurso, nombre, abreviatura, metrica, tipo, valor_x_hora)
            lista_recursos.append(recurso)
    
    def _guardar_categorias(self):
        root = ET.Element("listaCategorias")
        for categoria in lista_categorias:
            cat_elem = ET.SubElement(root, "categoria")
            cat_elem.set("id", categoria.id)
            ET.SubElement(cat_elem, "nombre").text = categoria.nombre
            ET.SubElement(cat_elem, "descripcion").text = categoria.descripcion
            ET.SubElement(cat_elem, "cargaTrabajo").text = categoria.carga_trabajo
            
            configs_elem = ET.SubElement(cat_elem, "listaConfiguraciones")
            for config in categoria.configuraciones:
                config_elem = ET.SubElement(configs_elem, "configuracion")
                config_elem.set("id", config.id)
                ET.SubElement(config_elem, "nombre").text = config.nombre
                ET.SubElement(config_elem, "descripcion").text = config.descripcion
                
                recursos_elem = ET.SubElement(config_elem, "recursosConfiguracion")
                for recurso_id, cantidad in config.recursos.items():
                    recurso_config_elem = ET.SubElement(recursos_elem, "recurso")
                    recurso_config_elem.set("id", recurso_id)
                    recurso_config_elem.text = str(cantidad)
        
        tree = ET.ElementTree(root)
        tree.write(f"{self.data_dir}/categorias.xml", encoding="utf-8", xml_declaration=True)
    
    def _cargar_categorias(self):
        if not os.path.exists(f"{self.data_dir}/categorias.xml"):
            return
        
        tree = ET.parse(f"{self.data_dir}/categorias.xml")
        root = tree.getroot()
        
        for categoria_elem in root.findall('categoria'):
            id_categoria = categoria_elem.get('id')
            nombre = categoria_elem.find('nombre').text
            descripcion = categoria_elem.find('descripcion').text
            carga_trabajo = categoria_elem.find('cargaTrabajo').text
            
            categoria = Categoria(id_categoria, nombre, descripcion, carga_trabajo)
            
            configs_elem = categoria_elem.find('listaConfiguraciones')
            if configs_elem is not None:
                for config_elem in configs_elem.findall('configuracion'):
                    id_config = config_elem.get('id')
                    nombre_config = config_elem.find('nombre').text
                    descripcion_config = config_elem.find('descripcion').text
                    
                    configuracion = Configuracion(id_config, nombre_config, descripcion_config)
                    
                    recursos_elem = config_elem.find('recursosConfiguracion')
                    if recursos_elem is not None:
                        for recurso_elem in recursos_elem.findall('recurso'):
                            recurso_id = recurso_elem.get('id')
                            cantidad = recurso_elem.text
                            configuracion.agregar_recurso(recurso_id, cantidad)
                    
                    categoria.agregar_configuracion(configuracion)
            
            lista_categorias.append(categoria)
    
    def _guardar_clientes(self):
        root = ET.Element("listaClientes")
        for cliente in lista_clientes:
            cliente_elem = ET.SubElement(root, "cliente")
            cliente_elem.set("nit", cliente.nit)
            ET.SubElement(cliente_elem, "nombre").text = cliente.nombre
            ET.SubElement(cliente_elem, "usuario").text = cliente.usuario
            ET.SubElement(cliente_elem, "clave").text = cliente.clave
            ET.SubElement(cliente_elem, "direccion").text = cliente.direccion
            ET.SubElement(cliente_elem, "correoElectronico").text = cliente.correo_electronico
            
            instancias_elem = ET.SubElement(cliente_elem, "listaInstancias")
            for instancia in cliente.instancias:
                instancia_elem = ET.SubElement(instancias_elem, "instancia")
                instancia_elem.set("id", instancia.id)
                ET.SubElement(instancia_elem, "idConfiguracion").text = instancia.id_configuracion
                ET.SubElement(instancia_elem, "nombre").text = instancia.nombre
                ET.SubElement(instancia_elem, "fechaInicio").text = str(instancia.fecha_inicio)
                ET.SubElement(instancia_elem, "estado").text = instancia.estado
                if instancia.fecha_final:
                    ET.SubElement(instancia_elem, "fechaFinal").text = str(instancia.fecha_final)
        
        tree = ET.ElementTree(root)
        tree.write(f"{self.data_dir}/clientes.xml", encoding="utf-8", xml_declaration=True)
    
    def _cargar_clientes(self):
        if not os.path.exists(f"{self.data_dir}/clientes.xml"):
            return
        
        tree = ET.parse(f"{self.data_dir}/clientes.xml")
        root = tree.getroot()
        
        for cliente_elem in root.findall('cliente'):
            nit = cliente_elem.get('nit')
            nombre = cliente_elem.find('nombre').text
            usuario = cliente_elem.find('usuario').text
            clave = cliente_elem.find('clave').text
            direccion = cliente_elem.find('direccion').text
            correo = cliente_elem.find('correoElectronico').text
            
            cliente = Cliente(nit, nombre, usuario, clave, direccion, correo)
            
            instancias_elem = cliente_elem.find('listaInstancias')
            if instancias_elem is not None:
                for instancia_elem in instancias_elem.findall('instancia'):
                    id_instancia = instancia_elem.get('id')
                    id_configuracion = instancia_elem.find('idConfiguracion').text
                    nombre_instancia = instancia_elem.find('nombre').text
                    fecha_inicio = instancia_elem.find('fechaInicio').text
                    estado = instancia_elem.find('estado').text
                    
                    fecha_final_elem = instancia_elem.find('fechaFinal')
                    fecha_final = fecha_final_elem.text if fecha_final_elem is not None else None
                    
                    instancia = Instancia(id_instancia, id_configuracion, nombre_instancia, fecha_inicio, estado, fecha_final)
                    cliente.agregar_instancia(instancia)
            
            lista_clientes.append(cliente)
    
    def _guardar_consumos(self):
        root = ET.Element("listadoConsumos")
        for consumo in lista_consumos:
            consumo_elem = ET.SubElement(root, "consumo")
            consumo_elem.set("nitCliente", consumo.nit_cliente)
            consumo_elem.set("idInstancia", consumo.id_instancia)
            ET.SubElement(consumo_elem, "tiempo").text = str(consumo.tiempo)
            ET.SubElement(consumo_elem, "fechahora").text = str(consumo.fecha_hora)
        
        tree = ET.ElementTree(root)
        tree.write(f"{self.data_dir}/consumos.xml", encoding="utf-8", xml_declaration=True)
    
    def _cargar_consumos(self):
        if not os.path.exists(f"{self.data_dir}/consumos.xml"):
            return
        
        tree = ET.parse(f"{self.data_dir}/consumos.xml")
        root = tree.getroot()
        
        for consumo_elem in root.findall('consumo'):
            nit_cliente = consumo_elem.get('nitCliente')
            id_instancia = consumo_elem.get('idInstancia')
            tiempo = consumo_elem.find('tiempo').text
            fecha_hora = consumo_elem.find('fechahora').text
            
            consumo = Consumo(nit_cliente, id_instancia, tiempo, fecha_hora)
            lista_consumos.append(consumo)
    
    def _guardar_facturas(self):
        root = ET.Element("listaFacturas")
        for factura in lista_facturas:
            factura_elem = ET.SubElement(root, "factura")
            factura_elem.set("numero", factura.numero)
            ET.SubElement(factura_elem, "nitCliente").text = factura.nit_cliente
            ET.SubElement(factura_elem, "fechaFactura").text = str(factura.fecha_factura)
            ET.SubElement(factura_elem, "montoTotal").text = str(factura.monto_total)
            
            detalles_elem = ET.SubElement(factura_elem, "detalles")
            for detalle in factura.detalles:
                detalle_elem = ET.SubElement(detalles_elem, "detalle")
                for key, value in detalle.items():
                    ET.SubElement(detalle_elem, key).text = str(value)
        
        tree = ET.ElementTree(root)
        tree.write(f"{self.data_dir}/facturas.xml", encoding="utf-8", xml_declaration=True)
    
    def _cargar_facturas(self):
        if not os.path.exists(f"{self.data_dir}/facturas.xml"):
            return
        
        tree = ET.parse(f"{self.data_dir}/facturas.xml")
        root = tree.getroot()
        
        for factura_elem in root.findall('factura'):
            numero = factura_elem.get('numero')
            nit_cliente = factura_elem.find('nitCliente').text
            fecha_factura = factura_elem.find('fechaFactura').text
            monto_total = factura_elem.find('montoTotal').text
            
            factura = Factura(numero, nit_cliente, fecha_factura, monto_total)
            
            detalles_elem = factura_elem.find('detalles')
            if detalles_elem is not None:
                for detalle_elem in detalles_elem.findall('detalle'):
                    detalle = {}
                    for child in detalle_elem:
                        detalle[child.tag] = child.text
                    factura.agregar_detalle(detalle)
            
            lista_facturas.append(factura)