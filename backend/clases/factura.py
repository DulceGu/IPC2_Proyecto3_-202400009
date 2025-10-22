from datetime import datetime

class Factura:
    def __init__(self, numero, nit_cliente, fecha_factura, monto_total):
        self.numero = numero
        self.nit_cliente = nit_cliente
        self.fecha_factura = fecha_factura
        self.monto_total = float(monto_total)
        self.detalles = []
    
    def agregar_detalle(self, detalle):
        self.detalles.append(detalle)
    
    def to_dict(self):
        return {
            'numero': self.numero,
            'nit_cliente': self.nit_cliente,
            'fecha_factura': str(self.fecha_factura),
            'monto_total': self.monto_total,
            'detalles': self.detalles
        }