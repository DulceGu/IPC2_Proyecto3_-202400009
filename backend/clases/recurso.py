class Recurso:
    def __init__(self, id, nombre, abreviatura, metrica, tipo, valor_x_hora):
        self.id = id
        self.nombre = nombre
        self.abreviatura = abreviatura
        self.metrica = metrica
        self.tipo = tipo
        self.valor_x_hora = float(valor_x_hora)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'abreviatura': self.abreviatura,
            'metrica': self.metrica,
            'tipo': self.tipo,
            'valor_x_hora': self.valor_x_hora
        }