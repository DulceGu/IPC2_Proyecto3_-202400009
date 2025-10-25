class Configuracion:
    def __init__(self, id, nombre, descripcion):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.recursos = {}  # Diccionario para almacenar recursos y sus cantidades
    
    def agregar_recurso(self, id_recurso, cantidad):
        print(f"Agregando recurso {id_recurso} con cantidad {cantidad} a configuración {self.id}")
        self.recursos[id_recurso] = float(cantidad)
        print(f"Recursos actuales en configuración {self.id}: {self.recursos}")

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'recursos': self.recursos
        }