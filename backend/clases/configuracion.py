class Configuracion:
    def __init__(self, id, nombre, descripcion):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.recursos = {}  # {id_recurso: cantidad}
    
    def agregar_recurso(self, id_recurso, cantidad):
        self.recursos[id_recurso] = float(cantidad)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'recursos': self.recursos
        }