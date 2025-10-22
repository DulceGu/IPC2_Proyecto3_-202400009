import re
from datetime import datetime

class Instancia:
    def __init__(self, id, id_configuracion, nombre, fecha_inicio, estado="Vigente", fecha_final=None):
        self.id = id
        self.id_configuracion = id_configuracion
        self.nombre = nombre
        self.fecha_inicio = self._extraer_fecha(fecha_inicio)
        self.estado = estado
        self.fecha_final = self._extraer_fecha(fecha_final) if fecha_final else None
        self.consumos = []
    
    def _extraer_fecha(self, texto):
        if texto is None:
            return None
        # Extraer fecha del formato dd/mm/yyyy
        patron = r'(\d{2}/\d{2}/\d{4})'
        coincidencias = re.findall(patron, str(texto))
        if coincidencias:
            try:
                return datetime.strptime(coincidencias[0], '%d/%m/%Y').date()
            except:
                return None
        return None
    
    def agregar_consumo(self, consumo):
        self.consumos.append(consumo)
    
    def to_dict(self):
        return {
            'id': self.id,
            'id_configuracion': self.id_configuracion,
            'nombre': self.nombre,
            'fecha_inicio': str(self.fecha_inicio) if self.fecha_inicio else None,
            'estado': self.estado,
            'fecha_final': str(self.fecha_final) if self.fecha_final else None
        }