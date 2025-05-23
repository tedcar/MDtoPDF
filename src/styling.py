from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors
from reportlab.lib.units import inch
import os
from .utils import resource_path # Import resource_path

# Font Registration
# Use resource_path to get the path to TimesNewRoman.ttf
# This ensures it works in both development and bundled (PyInstaller) mode.
# 'TimesNewRoman.ttf' is the name of the file as it will be in the bundle root,
# and also as it is expected to be found in src/ for development by resource_path.
actual_font_path = resource_path('TimesNewRoman.ttf')
times_new_roman_registered = False

if not os.path.exists(actual_font_path):
    print(f"Warning: Font {actual_font_path} not found (via resource_path). ReportLab may use a default font.")
else:
    try:
        pdfmetrics.registerFont(TTFont('TimesNewRoman', actual_font_path))
        times_new_roman_registered = True
        print(f"Successfully registered font: TimesNewRoman from {actual_font_path}")
    except Exception as e:
        print(f"Error registering TimesNewRoman from {actual_font_path}: {e}")

# Courier is a standard PDF font, so direct registration like above is not needed and can cause issues.
# We will directly use 'Courier' as the fontName in the style.

def get_base_style():
    default_font = 'Helvetica' # Absolute fallback
    if times_new_roman_registered:
        default_font = 'TimesNewRoman'
    
    return ParagraphStyle(
        name='Normal', 
        fontName=default_font, 
        fontSize=11,  
        leading=14,   
        alignment=TA_LEFT,
        textColor=colors.black,
        spaceAfter=6, 
        spaceBefore=6, 
    )

def get_all_styles():
    styles = {}
    base_style = get_base_style()
    styles['Normal'] = base_style

    styles['H1'] = ParagraphStyle(
        name='H1', parent=base_style, fontSize=20, leading=24, 
        spaceBefore=12, spaceAfter=10, textColor=colors.black
    )
    styles['H2'] = ParagraphStyle(
        name='H2', parent=base_style, fontSize=16, leading=19, 
        spaceBefore=10, spaceAfter=8, textColor=colors.black
    )
    styles['H3'] = ParagraphStyle(
        name='H3', parent=base_style, fontSize=14, leading=17, 
        spaceBefore=8, spaceAfter=6, textColor=colors.black
    )
    
    styles['Code'] = ParagraphStyle(
        name='Code', 
        fontName='Courier', # Directly specify Courier
        fontSize=9, leading=11,
        textColor=colors.darkgrey, backColor=colors.whitesmoke,
        leftIndent=12, rightIndent=12, spaceBefore=6, spaceAfter=6,
        borderPadding=2, borderColor=colors.lightgrey, borderWidth=0.5
    )
    styles['ListItem'] = ParagraphStyle( 
        name='ListItem', parent=base_style, leftIndent=18, bulletIndent=0, 
        firstLineIndent=0, spaceAfter=2, textColor=colors.black
    )
    styles['Bullet'] = styles['ListItem'] 
    styles['Blockquote'] = ParagraphStyle(
        name='Blockquote', parent=base_style, leftIndent=18, rightIndent=18,
        textColor=colors.dimgrey, spaceBefore=6, spaceAfter=6, 
        firstLineIndent=0, leading=base_style.leading * 1.1
    )
    return styles

def get_page_layout():
    return {
        'leftMargin': 1 * inch, 'rightMargin': 1 * inch, 
        'topMargin': 0.75 * inch, 'bottomMargin': 0.75 * inch,
    }
