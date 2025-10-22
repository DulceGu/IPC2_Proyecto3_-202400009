import re

def validar_nit(nit):
    patron = r'^\d+-[\dK]$'
    return bool(re.match(patron, nit))

def validar_fecha(texto):
    patron = r'(\d{2}/\d{2}/\d{4})'
    coincidencias = re.findall(patron, texto)
    return len(coincidencias) > 0

def validar_fecha_hora(texto):
    patron = r'(\d{2}/\d{2}/\d{4} \d{2}:\d{2})'
    coincidencias = re.findall(patron, texto)
    return len(coincidencias) > 0