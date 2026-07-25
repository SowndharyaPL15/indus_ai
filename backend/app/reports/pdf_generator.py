import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Define storage path
REPORTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../storage/reports"))
os.makedirs(REPORTS_DIR, exist_ok=True)

class PDFGenerator:
    def __init__(self, filename: str, report_id: str):
        self.filepath = os.path.join(REPORTS_DIR, filename)
        self.report_id = report_id
        self.doc = SimpleDocTemplate(
            self.filepath, 
            pagesize=letter,
            rightMargin=72, leftMargin=72,
            topMargin=72, bottomMargin=72
        )
        self.styles = getSampleStyleSheet()
        self.elements = []
        
        # Add custom styles
        self.styles.add(ParagraphStyle(name='SectionHeader', parent=self.styles['Heading2'], textColor=colors.HexColor("#1e3a8a"), spaceAfter=10))
        self.styles.add(ParagraphStyle(name='NormalText', parent=self.styles['Normal'], spaceAfter=10, leading=14))

    def _header_footer(self, canvas, doc):
        canvas.saveState()
        
        # Header
        canvas.setFont('Helvetica-Bold', 12)
        canvas.setFillColor(colors.HexColor("#1e3a8a"))
        canvas.drawString(doc.leftMargin, doc.height + doc.topMargin + 10, "INDUS AI")
        
        canvas.setFont('Helvetica', 10)
        canvas.setFillColor(colors.gray)
        canvas.drawRightString(doc.width + doc.leftMargin, doc.height + doc.topMargin + 10, "Industrial Decision Intelligence Platform")
        
        # Line below header
        canvas.setStrokeColor(colors.lightgrey)
        canvas.line(doc.leftMargin, doc.height + doc.topMargin, doc.width + doc.leftMargin, doc.height + doc.topMargin)
        
        # Footer
        canvas.line(doc.leftMargin, doc.bottomMargin - 10, doc.width + doc.leftMargin, doc.bottomMargin - 10)
        
        canvas.setFont('Helvetica', 8)
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        canvas.drawString(doc.leftMargin, doc.bottomMargin - 25, f"Generated: {timestamp}")
        
        canvas.drawCentredString(doc.width / 2.0 + doc.leftMargin, doc.bottomMargin - 25, f"Page {doc.page}")
        
        canvas.drawRightString(doc.width + doc.leftMargin, doc.bottomMargin - 25, f"Report ID: {self.report_id}")
        
        canvas.restoreState()

    def add_title(self, title: str):
        self.elements.append(Paragraph(title, self.styles['Title']))
        self.elements.append(Spacer(1, 0.2 * inch))

    def add_section(self, header: str, content: str):
        if not content:
            content = "N/A"
        self.elements.append(Paragraph(header, self.styles['SectionHeader']))
        
        # Handle simple newlines in text by splitting and adding as separate paragraphs
        for p_text in str(content).split('\n'):
            if p_text.strip():
                self.elements.append(Paragraph(p_text.strip(), self.styles['NormalText']))
        self.elements.append(Spacer(1, 0.1 * inch))
        
    def add_list_section(self, header: str, items: list):
        self.elements.append(Paragraph(header, self.styles['SectionHeader']))
        if not items:
            self.elements.append(Paragraph("None recorded.", self.styles['NormalText']))
        else:
            for item in items:
                self.elements.append(Paragraph(f"• {item}", self.styles['NormalText']))
        self.elements.append(Spacer(1, 0.1 * inch))

    def add_table_section(self, header: str, data: list):
        self.elements.append(Paragraph(header, self.styles['SectionHeader']))
        if not data or len(data) <= 1:
            self.elements.append(Paragraph("No data available.", self.styles['NormalText']))
        else:
            table = Table(data, colWidths=[1.5*inch, 2*inch, 2.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
                ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ]))
            self.elements.append(table)
        self.elements.append(Spacer(1, 0.1 * inch))

    def add_page_break(self):
        self.elements.append(PageBreak())

    def generate(self) -> str:
        self.doc.build(self.elements, onFirstPage=self._header_footer, onLaterPages=self._header_footer)
        return self.filepath
