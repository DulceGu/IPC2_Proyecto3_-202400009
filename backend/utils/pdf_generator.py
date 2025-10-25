from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime

class PDFGenerator:
    @staticmethod
    def generar_detalle_factura(factura, cliente, output_path):
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Título
        title = Paragraph("DETALLE DE FACTURA", styles['Heading1'])
        elements.append(title)
        elements.append(Spacer(1, 0.2*inch))
        
        # Información de la factura
        info_data = [
            ['Número de Factura:', factura.numero],
            ['Cliente:', cliente.nombre],
            ['NIT:', cliente.nit],
            ['Fecha de Factura:', str(factura.fecha_factura)],
            ['Monto Total:', f"Q {factura.monto_total:.2f}"]
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Detalles de la factura
        if factura.detalles:
            detalles_header = ['Instancia', 'Recurso', 'Cantidad', 'Tiempo (h)', 'Valor x Hora', 'Subtotal']
            detalles_data = [detalles_header]
            
            for detalle in factura.detalles:
                detalles_data.append([
                    detalle.get('nombre_instancia', ''),
                    detalle.get('nombre_recurso', ''),
                    detalle.get('cantidad', ''),
                    detalle.get('tiempo', ''),
                    f"Q {float(detalle.get('valor_x_hora', 0)):.2f}",
                    f"Q {float(detalle.get('subtotal', 0)):.2f}"
                ])
            
            detalles_table = Table(detalles_data, colWidths=[1*inch, 1.5*inch, 0.8*inch, 0.8*inch, 1*inch, 1*inch])
            detalles_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(detalles_table)
        
        doc.build(elements)
    
    @staticmethod
    def generar_analisis_ventas(tipo, datos, rango_fechas, output_path):
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        title = Paragraph(f"ANÁLISIS DE VENTAS - {tipo.upper()}", styles['Heading1'])
        elements.append(title)
        elements.append(Spacer(1, 0.2*inch))
        
        # Rango de fechas
        fecha_info = Paragraph(f"Rango: {rango_fechas['inicio']} a {rango_fechas['fin']}", styles['Normal'])
        elements.append(fecha_info)
        elements.append(Spacer(1, 0.3*inch))
        
        # Tabla de datos
        if datos:
            headers = list(datos[0].keys())
            table_data = [headers]
            
            for item in datos:
                row = []
                for key in headers:
                    value = item.get(key, '')
                    if 'monto' in key.lower() or 'total' in key.lower():
                        value = f"Q {float(value):.2f}"
                    row.append(str(value))
                table_data.append(row)
            
            table = Table(table_data, colWidths=[1.5*inch] * len(headers))
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(table)
        
        doc.build(elements)