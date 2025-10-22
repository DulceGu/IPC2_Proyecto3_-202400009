import re
from datetime import datetime

class Consumo:
    def __init__(self, nit_cliente, id_instancia, tiempo, fecha_hora):
        self.nit_cliente = nit_cliente
        self.id_instancia = id_instancia
        self.tiempo = float(tiempo)
        self.fecha_hora = self._extraer_fecha_hora(fecha_hora)
    
    def _extraer_fecha_hora(self, texto):
        if texto is None:
            return None
        # Extraer fecha y hora del formato dd/mm/yyyy hh:mi
        patron = r'(\d{2}/\d{2}/\d{4} \d{2}:\d{2})'
        coincidencias = re.findall(patron, str(texto))
        if coincidencias:
            try:
                return datetime.strptime(coincidencias[0], '%d/%m/%Y %H:%M')
            except:
                return None
        return None
    
    def to_dict(self):
        return {
            'nit_cliente': self.nit_cliente,
            'id_instancia': self.id_instancia,
            'tiempo': self.tiempo,
            'fecha_hora': str(self.fecha_hora) if self.fecha_hora else None
        }