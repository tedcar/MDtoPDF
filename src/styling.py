from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.colors import black
from reportlab.lib.units import inch

# Register the Verdana font (which is commonly available on Windows systems)
pdfmetrics.registerFont(TTFont('Verdana', 'C:/Windows/Fonts/Verdana.ttf'))

def get_bible_style():
    return ParagraphStyle(
        name='BibleStyle',
        fontName='Verdana',
        fontSize=12,  # Increased font size
        leading=18,   # Increased line spacing
        alignment=TA_JUSTIFY,  # Changed to justified alignment
        textColor=black,
        spaceAfter=10,
        spaceBefore=10,
    )

def get_page_layout():
    return {
        'leftMargin': 1.25 * inch,  # Reduced left margin
        'rightMargin': 1.25 * inch, # Reduced right margin
        'topMargin': 0.75 * inch,   # Reduced top margin
        'bottomMargin': 0.75 * inch, # Reduced bottom margin
    }