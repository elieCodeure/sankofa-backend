import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.units import cm
from django.conf import settings
import os

def generate_invoice_pdf(order):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor("#C18B51"), # Sankhofa Gold
        spaceAfter=20,
        fontName='Helvetica-Bold'
    )
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.grey,
        leading=14
    )

    elements = []

    # 1. Header (Brand)
    elements.append(Paragraph("SANKHOFA", title_style))
    elements.append(Paragraph("Les Trésors de l'Afrique — Artisanal & Premium", header_style))
    elements.append(Spacer(1, 1*cm))

    # 2. Order Info & Customer Details
    col_data = [
        [
            Paragraph(f"<b>FACTURE #{order.id}</b><br/>Date: {order.created_at.strftime('%d/%m/%Y')}", styles['Normal']),
            Paragraph(f"<b>CLIENT</b><br/>{order.user.get_full_name() or order.user.email}<br/>{order.shipping_address}<br/>Tél: {order.phone_number}", styles['Normal'])
        ]
    ]
    info_table = Table(col_data, colWidths=[9*cm, 8*cm])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 1*cm))

    # 3. Items Table
    table_data = [["Désignation", "Quantité", "Prix Unit.", "Total"]]
    currency = "EUR"
    if order.items.exists() and order.items.first().product:
        currency = order.items.first().product.currency
        
    for item in order.items.all():
        table_data.append([
            item.product_name,
            str(item.quantity),
            f"{item.price} {currency}",
            f"{item.price * item.quantity} {currency}"
        ])
    
    # Add Space and Total
    table_data.append(["", "", "", ""])
    table_data.append(["", "", "TOTAL", f"{order.total_price} {currency}"])

    items_table = Table(table_data, colWidths=[9*cm, 2*cm, 3*cm, 3*cm])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1A1A1A")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#F9F9F9")),
        ('FONTNAME', (2, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor("#C18B51")),
    ]))
    elements.append(items_table)
    
    # 4. Footer
    elements.append(Spacer(1, 2*cm))
    footer_text = "Merci pour votre confiance. En achetant sur Sankhofa, vous soutenez l'artisanat local africain."
    elements.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, alignment=1, textColor=colors.grey)))

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
