class Cliente:
    def __init__(self, nit, nombre, usuario, clave, direccion, correo_electronico):
        self.nit = nit
        self.nombre = nombre
        self.usuario = usuario
        self.clave = clave
        self.direccion = direccion
        self.correo_electronico = correo_electronico
        self.instancias = []
    
    def agregar_instancia(self, instancia):
        self.instancias.append(instancia)
    
    def to_dict(self):
        return {
            'nit': self.nit,
            'nombre': self.nombre,
            'usuario': self.usuario,
            'direccion': self.direccion,
            'correo_electronico': self.correo_electronico,
            'instancias': [instancia.to_dict() for instancia in self.instancias]
        }