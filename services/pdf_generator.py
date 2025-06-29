from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from pathlib import Path
import os
from datetime import datetime


class InvoicePDFGenerator:
    """Generate PDF invoices using ReportLab"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Set up custom paragraph styles"""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        self.header_style = ParagraphStyle(
            'CustomHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        self.right_align_style = ParagraphStyle(
            'RightAlign',
            parent=self.styles['Normal'],
            alignment=TA_RIGHT
        )
    
    def generate_invoice_pdf(self, invoice, company, invoice_items, output_path):
        """Generate a PDF invoice"""
        
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Create the PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build the story (content)
        story = []
        
        # Title
        story.append(Paragraph("INVOICE", self.title_style))
        story.append(Spacer(1, 20))
        
        # Invoice header info
        header_data = [
            ['Invoice Number:', invoice.invoice_number],
            ['Invoice Date:', invoice.invoice_date.strftime('%Y-%m-%d')],
            ['Due Date:', invoice.due_date.strftime('%Y-%m-%d') if invoice.due_date else 'N/A'],
            ['Status:', invoice.status.value.title()]
        ]
        
        header_table = Table(header_data, colWidths=[2*inch, 2*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(header_table)
        story.append(Spacer(1, 30))
        
        # Bill To section
        story.append(Paragraph("Bill To:", self.header_style))
        
        bill_to_text = f"""
        <b>{company.name}</b><br/>
        {company.contact_person or ''}<br/>
        {company.email or ''}<br/>
        {company.phone or ''}<br/>
        {company.formatted_address or ''}
        """
        
        story.append(Paragraph(bill_to_text, self.styles['Normal']))
        story.append(Spacer(1, 30))
        
        # Invoice items table
        story.append(Paragraph("Invoice Items:", self.header_style))
        
        # Prepare table data
        table_data = [['Description', 'Quantity', 'Rate', 'Amount']]
        
        for item in invoice_items:
            table_data.append([
                Paragraph(item.description, self.styles['Normal']),
                f"{item.quantity}",
                f"${item.unit_price/100:.2f}",
                f"${item.total_amount/100:.2f}"
            ])
        
        # Add subtotal, tax, and total rows
        table_data.append(['', '', 'Subtotal:', f"${invoice.subtotal/100:.2f}"])
        
        if invoice.tax_amount > 0:
            tax_rate = invoice.tax_rate / 100 if invoice.tax_rate else 0  # Convert from basis points
            table_data.append(['', '', f'Tax ({tax_rate:.2f}%):', f"${invoice.tax_amount/100:.2f}"])
        
        table_data.append(['', '', 'Total:', f"${invoice.total_amount/100:.2f}"])
        
        # Create the table
        items_table = Table(table_data, colWidths=[4*inch, 1*inch, 1*inch, 1*inch])
        items_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -4), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -4), 10),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            
            # Subtotal/tax/total rows
            ('FONTNAME', (0, -3), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -3), (-1, -1), 10),
            ('ALIGN', (2, -3), (-1, -1), 'RIGHT'),
            
            # Total row highlight
            ('BACKGROUND', (2, -1), (-1, -1), colors.lightgrey),
            
            # Grid
            ('GRID', (0, 0), (-1, -4), 1, colors.black),
            ('LINEBELOW', (2, -3), (-1, -1), 1, colors.black),
            
            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(items_table)
        story.append(Spacer(1, 30))
        
        # Notes section
        if invoice.notes:
            story.append(Paragraph("Notes:", self.header_style))
            story.append(Paragraph(invoice.notes, self.styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Terms section
        if invoice.terms:
            story.append(Paragraph("Terms:", self.header_style))
            story.append(Paragraph(invoice.terms, self.styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Footer
        footer_text = f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        story.append(Spacer(1, 40))
        story.append(Paragraph(footer_text, self.right_align_style))
        
        # Build the PDF
        doc.build(story)
        
        return output_path 