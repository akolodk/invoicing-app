from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, BaseDocTemplate, PageTemplate, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from pathlib import Path
import os
from datetime import datetime


class PolishInvoicePDFGenerator:
    """Generate Polish PDF invoices (Faktura) using ReportLab"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_fonts()
        self.setup_custom_styles()
    
    def setup_fonts(self):
        """Setup fonts for Polish characters"""
        try:
            # Register DejaVu fonts that support Polish characters
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            
            # Try to register DejaVu fonts
            normal_font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
            bold_font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
            
            fonts_registered = 0
            
            # Register normal font
            if os.path.exists(normal_font_path):
                try:
                    pdfmetrics.registerFont(TTFont('DejaVuSans', normal_font_path))
                    fonts_registered += 1
                    print(f"Registered font: DejaVuSans")
                except Exception as e:
                    print(f"Error registering DejaVuSans: {e}")
            
            # Register bold font
            if os.path.exists(bold_font_path):
                try:
                    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', bold_font_path))
                    fonts_registered += 1
                    print(f"Registered font: DejaVuSans-Bold")
                except Exception as e:
                    print(f"Error registering DejaVuSans-Bold: {e}")
            
            # Set font availability flag
            self.has_polish_fonts = fonts_registered > 0
            print(f"Polish fonts available: {self.has_polish_fonts} ({fonts_registered} fonts registered)")
                        
        except Exception as e:
            print(f"Font setup error: {e}")
            self.has_polish_fonts = False
    
    def create_background_canvas(self, background_image_path):
        """Create a canvas with background image drawn properly"""
        class BackgroundCanvas(canvas.Canvas):
            def __init__(self, filename, **kwargs):
                canvas.Canvas.__init__(self, filename, **kwargs)
                self.background_image = background_image_path
                
            def showPage(self):
                """Draw background before showing page"""
                if self.background_image and os.path.exists(self.background_image):
                    try:
                        # Get page dimensions
                        page_width, page_height = A4
                        header_height = 4*cm
                        
                        # Draw the header image at the top of the page
                        # Position it so the top of the image aligns with the top of the page
                        self.drawImage(
                            self.background_image,
                            0, page_height - header_height,  # Position at top
                            width=page_width,
                            height=header_height,
                            preserveAspectRatio=False,
                            mask='auto'
                        )
                        
                        print(f"Header image drawn at: (0, {page_height - header_height}) size: {page_width}x{header_height}")
                    except Exception as e:
                        print(f"Error drawing header image: {e}")
                        import traceback
                        traceback.print_exc()
                
                # Call parent method to finalize the page
                canvas.Canvas.showPage(self)
        
        return BackgroundCanvas
    
    def setup_custom_styles(self):
        """Set up custom paragraph styles for Polish invoice"""
        # Choose font based on availability
        normal_font = 'DejaVuSans' if getattr(self, 'has_polish_fonts', False) else 'Helvetica'
        bold_font = 'DejaVuSans-Bold' if getattr(self, 'has_polish_fonts', False) else 'Helvetica-Bold'
        
        self.title_style = ParagraphStyle(
            'PolishTitle',
            parent=self.styles['Heading1'],
            fontSize=20,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.black,
            fontName=bold_font
        )
        
        self.header_style = ParagraphStyle(
            'PolishHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceAfter=8,
            textColor=colors.black,
            fontName=bold_font
        )
        
        self.normal_style = ParagraphStyle(
            'PolishNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName=normal_font
        )
        
        self.small_style = ParagraphStyle(
            'PolishSmall',
            parent=self.styles['Normal'],
            fontSize=8,
            fontName=normal_font
        )
        
        self.right_align_style = ParagraphStyle(
            'PolishRightAlign',
            parent=self.styles['Normal'],
            alignment=TA_RIGHT,
            fontSize=10,
            fontName=normal_font
        )
    
    def generate_polish_invoice_pdf(self, invoice, company, invoice_items, output_path, seller_info=None):
        """Generate a Polish PDF invoice (Faktura)"""
        
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Check for background header image
        header_image_path = None
        
        # Try to find header image in different locations
        possible_header_paths = [
            "assets/invoice_header.png",
            "assets/invoice_header.jpg", 
            "assets/invoice_header.jpeg"
        ]
        
        for path in possible_header_paths:
            if os.path.exists(path):
                header_image_path = path
                break
        
        # Create the PDF document with A4 size
        if header_image_path:
            print(f"Using background image: {header_image_path}")
            BackgroundCanvas = self.create_background_canvas(header_image_path)
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=4*cm,  # More space from top to account for header
                bottomMargin=2*cm,
                canvasmaker=BackgroundCanvas
            )
        else:
            print("No background image found, using standard layout")
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
        
        # Build the story (content)
        story = []
        
        # Add branded header only if NO background image is available
        if not header_image_path and seller_info and seller_info.get('header_title'):
            header_style = ParagraphStyle(
                'BrandHeader',
                parent=self.styles['Normal'],
                fontSize=24,
                textColor=colors.HexColor('#FF6B35'),  # Orange color similar to the image
                fontName='Helvetica-Bold',
                alignment=TA_RIGHT,
                spaceAfter=5
            )
            
            subtitle_style = ParagraphStyle(
                'BrandSubtitle',
                parent=self.styles['Normal'],
                fontSize=14,
                textColor=colors.HexColor('#FF6B35'),
                fontName='Helvetica',
                alignment=TA_RIGHT,
                spaceAfter=10
            )
            
            desc_style = ParagraphStyle(
                'BrandDescription',
                parent=self.styles['Normal'],
                fontSize=8,
                textColor=colors.grey,
                fontName='Helvetica',
                alignment=TA_LEFT,
                spaceAfter=20
            )
            
            # Header with branding
            story.append(Paragraph(seller_info.get('header_title', ''), header_style))
            story.append(Paragraph(seller_info.get('header_subtitle', ''), subtitle_style))
            story.append(Paragraph(seller_info.get('header_description', ''), desc_style))
        
        # Add space from top if using background image
        if header_image_path:
            story.append(Spacer(1, 1*cm))  # Extra space to avoid overlapping with header image
        
        # Title
        story.append(Paragraph("FAKTURA", self.title_style))
        story.append(Spacer(1, 15))
        
        # Polish month names for proper date formatting
        polish_months = {
            1: 'stycznia', 2: 'lutego', 3: 'marca', 4: 'kwietnia', 5: 'maja', 6: 'czerwca',
            7: 'lipca', 8: 'sierpnia', 9: 'września', 10: 'października', 11: 'listopada', 12: 'grudnia'
        }
        
        def format_polish_date(date_obj):
            if not date_obj:
                return 'Nie określono'
            day = date_obj.day
            month = polish_months[date_obj.month]
            year = date_obj.year
            return f"{day} {month} {year}"
        
        # Invoice basic info table with proper formatting
        formatted_invoice_number = f"Faktura VAT nr {invoice.invoice_number}/oryginał"
        
        invoice_info_data = [
            ['', formatted_invoice_number],
            ['', format_polish_date(invoice.invoice_date)]
        ]
        
        invoice_info_table = Table(invoice_info_data, colWidths=[14*cm, 6*cm])
        # Choose font based on availability for table
        table_bold_font = 'DejaVuSans-Bold' if getattr(self, 'has_polish_fonts', False) else 'Helvetica-Bold'
        
        invoice_info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), table_bold_font),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        story.append(invoice_info_table)
        story.append(Spacer(1, 20))
        
        # Seller and Buyer section
        col_width = (A4[0] - 4*cm) / 2 - 1*cm
        
        # Default seller info if not provided
        if not seller_info:
            seller_info = {
                'name': 'Twoja Firma Sp. z o.o.',
                'address': 'ul. Przykładowa 123',
                'city': '00-000 Warszawa',
                'nip': '123-456-78-90',
                'regon': '123456789',
                'phone': '+48 22 123 45 67',
                'email': 'kontakt@twojafirma.pl'
            }
        
        # Format seller info to match the example
        seller_lines = [
            f"<b>Sprzedawca:</b>",
            f"<b>{seller_info.get('name', '')}</b>"
        ]
        
        # Add business type if available
        if seller_info.get('business_type'):
            seller_lines.append(f"<b>{seller_info.get('business_type', '')}</b>")
        
        # Add address
        seller_lines.extend([
            f"{seller_info.get('city', '')}, {seller_info.get('address', '')}",
            f"NIP: {seller_info.get('nip', '')}"
        ])
        
        # Add bank info if available
        if seller_info.get('bank_name') and seller_info.get('bank_account'):
            seller_lines.append(f"Bank: {seller_info.get('bank_name', '')} Nr rachunku: {seller_info.get('bank_account', '')}")
        
        # Add contact info if available
        if seller_info.get('phone'):
            seller_lines.append(f"Tel: {seller_info.get('phone', '')}")
        if seller_info.get('email'):
            seller_lines.append(f"Email: {seller_info.get('email', '')}")
        
        seller_text = "<br/>".join(seller_lines)
        
        # Format buyer info to match the example
        buyer_lines = [
            f"<b>Nabywca:</b>",
            f"<b>{company.name}</b>"
        ]
        
        # Add contact person if available
        if company.contact_person:
            buyer_lines.append(company.contact_person)
        
        # Add address
        if company.formatted_address:
            buyer_lines.append(company.formatted_address)
        
        # Add NIP
        buyer_lines.append(f"NIP: {getattr(company, 'tax_id', '') or 'Nie podano'}")
        
        # Add contact info if available
        if company.phone:
            buyer_lines.append(f"Tel: {company.phone}")
        if company.email:
            buyer_lines.append(f"Email: {company.email}")
        
        buyer_text = "<br/>".join(buyer_lines)
        
        # Create table with seller and buyer info
        seller_buyer_table = Table(
            [[Paragraph(seller_text, self.normal_style), 
              Paragraph(buyer_text, self.normal_style)]],
            colWidths=[col_width, col_width]
        )
        
        seller_buyer_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        story.append(seller_buyer_table)
        story.append(Spacer(1, 20))
        
        # Invoice items table header
        story.append(Paragraph("POZYCJE FAKTURY:", self.header_style))
        story.append(Spacer(1, 10))
        
        # Prepare items table data
        table_data = [
            ['Lp.', 'Nazwa towaru/usługi', 'Ilość', 'J.m.', 'Cena netto', 'VAT %', 'Kwota VAT', 'Wartość brutto']
        ]
        
        # Calculate totals
        net_total = 0
        vat_total = 0
        gross_total = 0
        
        for idx, item in enumerate(invoice_items, 1):
            # Calculate VAT
            net_amount = item.total_amount  # This is stored in cents
            vat_rate = invoice.tax_rate / 100 if invoice.tax_rate else 0  # Convert from basis points to percentage
            vat_amount = int(net_amount * vat_rate / 100) if vat_rate > 0 else 0
            gross_amount = net_amount + vat_amount
            
            # Format unit of measure
            unit_measure = 'godz.' if 'godzin' in item.description.lower() or 'hour' in item.description.lower() else 'szt.'
            
            table_data.append([
                str(idx),
                Paragraph(item.description, self.small_style),
                f"{item.quantity:.2f}",
                unit_measure,
                f"{net_amount/100:.2f} zł",
                f"{vat_rate:.0f}%" if vat_rate > 0 else "0%",
                f"{vat_amount/100:.2f} zł",
                f"{gross_amount/100:.2f} zł"
            ])
            
            net_total += net_amount
            vat_total += vat_amount
            gross_total += gross_amount
        
        # Add summary rows
        table_data.append(['', '', '', '', '', '', '', ''])  # Empty row
        table_data.append(['', 'RAZEM:', '', '', f"{net_total/100:.2f} zł", '', f"{vat_total/100:.2f} zł", f"{gross_total/100:.2f} zł"])
        
        # Create the items table
        items_table = Table(table_data, colWidths=[1*cm, 6*cm, 1.5*cm, 1*cm, 2*cm, 1.5*cm, 2*cm, 2.5*cm])
        
        # Use Polish-compatible fonts for table
        table_normal_font = 'DejaVuSans' if getattr(self, 'has_polish_fonts', False) else 'Helvetica'
        table_bold_font = 'DejaVuSans-Bold' if getattr(self, 'has_polish_fonts', False) else 'Helvetica-Bold'
        
        items_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), table_bold_font),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -3), table_normal_font),
            ('FONTSIZE', (0, 1), (-1, -3), 8),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Lp. column
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),  # Numeric columns
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),    # Description column
            
            # Summary row
            ('FONTNAME', (0, -1), (-1, -1), table_bold_font),
            ('FONTSIZE', (0, -1), (-1, -1), 9),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            
            # Grid
            ('GRID', (0, 0), (-1, -2), 0.5, colors.black),
            ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
            ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
            
            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ]))
        
        story.append(items_table)
        story.append(Spacer(1, 20))
        
        # Additional invoice details table (like in the example)
        additional_info_data = [
            ['Data sprzedaży:', format_polish_date(invoice.invoice_date)],
            ['Sposób zapłaty:', 'Przelew'],
            ['Termin płatności:', format_polish_date(invoice.due_date)],
            ['Uwagi:', invoice.notes if invoice.notes else '']
        ]
        
        # Only add rows that have content
        filtered_info_data = [row for row in additional_info_data if row[1]]
        
        if filtered_info_data:
            info_table = Table(filtered_info_data, colWidths=[4*cm, 10*cm])
            info_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), table_bold_font),
                ('FONTNAME', (1, 0), (1, -1), table_normal_font),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ]))
            
            story.append(info_table)
            story.append(Spacer(1, 20))
        
        # Summary section
        summary_text = f"""
        <b>PODSUMOWANIE:</b><br/>
        Wartość netto: {net_total/100:.2f} zł<br/>
        VAT: {vat_total/100:.2f} zł<br/>
        <b>Do zapłaty: {gross_total/100:.2f} zł</b>
        """
        
        story.append(Paragraph(summary_text, self.normal_style))
        story.append(Spacer(1, 30))
        
        # Signature section - simplified like in the example
        signature_data = [
            ['Faktura bez podpisu odbiorcy', 'Osoba upoważniona do wystawienia faktury VAT'],
            ['', ''],
            ['', seller_info.get('name', '').split()[0] + ' ' + seller_info.get('name', '').split()[1] if len(seller_info.get('name', '').split()) > 1 else seller_info.get('name', '')]
        ]
        
        signature_table = Table(signature_data, colWidths=[8*cm, 8*cm])
        signature_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('ALIGN', (0, 2), (1, 2), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), table_normal_font),
            ('FONTNAME', (0, 2), (1, 2), table_normal_font),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, 1), 20),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        story.append(signature_table)
        
        # Footer
        footer_text = f"Faktura wygenerowana: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        story.append(Spacer(1, 20))
        story.append(Paragraph(footer_text, self.right_align_style))
        
        # Build the PDF
        doc.build(story)
        
        return output_path
    
    def get_amount_in_words_polish(self, amount):
        """Convert amount to words in Polish (basic implementation)"""
        # This is a simplified version - for production, you might want to use a proper library
        # like 'num2words' with Polish support
        return f"{amount/100:.2f} złotych" 