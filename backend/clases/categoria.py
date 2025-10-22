class Categoria:
    def __init__(self, id, nombre, descripcion, carga_trabajo):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.carga_trabajo = carga_trabajo
        self.configuraciones = []
    
    def agregar_configuracion(self, configuracion):
        self.configuraciones.append(configuracion)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'carga_trabajo': self.carga_trabajo,
            'configuraciones': [config.to_dict() for config in self.configuraciones]
        }