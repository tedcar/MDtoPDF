import markdown
import pdfkit
import requests
from bs4 import BeautifulSoup
import base64
import os
from PyQt5.QtWidgets import QMessageBox
import logging
import sys
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from PIL import Image as PILImage
import re

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Modify get_wkhtmltopdf_path to check WKHTMLTOPDF_PATH environment variable
def get_wkhtmltopdf_path():
    # Check environment variable first
    env_path = os.getenv('WKHTMLTOPDF_PATH')
    if env_path and os.path.exists(env_path):
        return env_path
    possible_paths = [
        r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe',  # Windows
        r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe',  # Windows 32-bit
        '/usr/local/bin/wkhtmltopdf',  # macOS
        '/usr/bin/wkhtmltopdf',  # Linux
        # Add any other relevant paths here
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

def strip_emojis(text):
    """Remove emojis from the text."""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Symbols & Pictographs
        "\U0001F680-\U0001F6FF"  # Transport & Map Symbols
        "\U0001F1E0-\U0001F1FF"  # Flags
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text)

def convert_md_to_pdf(input_file, output_file, progress_callback=None, error_callback=None):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        logger.info("Processing Markdown content")
        md_content = strip_emojis(md_content)
        html_content = markdown.markdown(md_content, extensions=['extra', 'codehilite'])
        
        wkhtmltopdf_path = get_wkhtmltopdf_path()
        if wkhtmltopdf_path:
            config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
            pdfkit.from_string(html_content, output_file, configuration=config)
        else:
            logger.error("wkhtmltopdf not found. Please install it for better PDF conversion results.")
            if error_callback:
                error_callback("wkhtmltopdf is not installed. Please install it to enhance PDF conversion quality.")
        
        logger.info(f"Successfully converted {input_file} to {output_file}")
        if progress_callback:
            progress_callback(100)
        return output_file
    except Exception as e:
        logger.error(f"Error converting {input_file} to PDF: {e}")
        if progress_callback:
            progress_callback(-1)  # Indicate error in progress
        if error_callback:
            error_callback(str(e))
        raise

def create_pdf_with_reportlab(html_content, output_file):
    try:
        doc = SimpleDocTemplate(output_file, pagesize=letter, 
                                rightMargin=72, leftMargin=72, 
                                topMargin=72, bottomMargin=18)
        styles = getSampleStyleSheet()
        custom_styles = {}
        
        # Define CustomBody style
        if 'SegoeUIEmoji' in pdfmetrics.getRegisteredFontNames():
            custom_body_style = ParagraphStyle(
                name='CustomBody', 
                fontName='SegoeUIEmoji', 
                fontSize=12,  # Increased font size for better visibility
                leading=16,    # Increased leading for better readability
                spaceAfter=12
            )
        else:
            custom_body_style = ParagraphStyle(
                name='CustomBody', 
                fontName='Helvetica', 
                fontSize=12,  # Increased font size
                leading=16,    # Increased leading
                spaceAfter=12
            )
        styles.add(custom_body_style)
        custom_styles['CustomBody'] = custom_body_style
        
        # Define CustomHeading1 to CustomHeading6 styles
        for i in range(1, 7):
            style_name = f'CustomHeading{i}'
            styles.add(ParagraphStyle(
                name=style_name,
                parent=styles['Heading1'],
                fontName='Helvetica-Bold',
                fontSize=20 - (i-1)*2,  # Further increased font sizes
                leading=24 - (i-1)*2,
                spaceAfter=12
            ))
            custom_styles[style_name] = styles[style_name]
        
        # Define CustomCode style
        styles.add(ParagraphStyle(
            name='CustomCode',
            fontName='Courier',
            fontSize=10,
            leading=12,
            spaceAfter=12
        ))
        custom_styles['CustomCode'] = styles['CustomCode']
        
        # Add border around content
        from reportlab.lib import colors
        from reportlab.platypus import Frame, PageTemplate
        
        story = []
    
        soup = BeautifulSoup(html_content, 'html.parser')
        for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'img', 'pre', 'code']):
            if element.name == 'img':
                img_data = process_image(element['src'])
                if img_data:
                    try:
                        img = Image(BytesIO(img_data))
                        img_width, img_height = PILImage.open(BytesIO(img_data)).size
                        aspect = img_height / float(img_width)
                        img.drawWidth = 6*inch
                        img.drawHeight = 6*inch * aspect
                        story.append(img)
                        story.append(Spacer(1, 12))
                    except Exception as e:
                        logger.error(f"Failed to add image to PDF: {e}")
                        show_error_message(f"Failed to add image to PDF: {e}")
            elif element.name in ['pre', 'code']:
                style = styles.get('CustomCode', styles['Normal'])
                text = element.get_text()
                story.append(Paragraph(text, style))
                story.append(Spacer(1, 12))
            else:
                if element.name.startswith('h') and len(element.name) == 2 and element.name[1].isdigit():
                    heading_level = int(element.name[1])
                    style_name = f'CustomHeading{heading_level}'
                else:
                    style_name = 'CustomBody'
                style = styles.get(style_name, styles['CustomBody'])
                text = element.get_text()
                story.append(Paragraph(text, style))
                if element.name.startswith('h'):
                    story.append(Spacer(1, 6))
                else:
                    story.append(Spacer(1, 12))
    
            # Add page break after h1 elements
            if element.name == 'h1':
                story.append(PageBreak())
        
        # Create a frame with border
        frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
        template = PageTemplate(id='with_border', frames=[frame],
                                onPage=add_border)
        doc.addPageTemplates([template])
        
        doc.build(story)
        logger.info("ReportLab PDF creation succeeded.")
    except KeyError as ke:
        missing_style = ke.args[0].split("'")[1]
        logger.error(f"Style '{missing_style}' not found in stylesheet.")
        show_error_message(f"Style '{missing_style}' not found in stylesheet.")
    except Exception as e:
        logger.error(f"Error creating PDF with ReportLab: {e}")
        show_error_message(f"Error creating PDF: {e}")

def process_image(src):
    logger.info(f"Processing image: {src}")
    if src.startswith(('http://', 'https://')):
        try:
            response = requests.get(src, timeout=10)
            response.raise_for_status()
            img_data = response.content
            logger.info(f"Successfully fetched image from {src}")
            return optimize_image(img_data)
        except Exception as e:
            logger.error(f"Failed to fetch image: {src}. Error: {e}")
    else:
        try:
            if not os.path.isabs(src):
                # Assuming relative path from execution directory
                src = os.path.abspath(src)
            with open(src, 'rb') as img_file:
                img_data = img_file.read()
            logger.info(f"Successfully read local image: {src}")
            return optimize_image(img_data)
        except Exception as e:
            logger.error(f"Failed to read image: {src}. Error: {e}")
    return None

def optimize_image(img_data):
    try:
        img = PILImage.open(BytesIO(img_data))
        img = img.convert('RGB')
        output = BytesIO()
        img.save(output, format='JPEG', quality=85, optimize=True)
        logger.info("Image optimized successfully")
        return output.getvalue()
    except Exception as e:
        logger.error(f"Failed to optimize image: {e}")
        return img_data

def add_border(canvas, doc):
    """Draw a border around each page."""
    canvas.saveState()
    border_width = 2
    canvas.setStrokeColor(colors.HexColor("#333333"))  # Dark gray border
    canvas.setLineWidth(border_width)
    canvas.rect(doc.leftMargin, doc.bottomMargin, doc.width, doc.height)
    canvas.restoreState()

# GUI-related functions (implement in gui.py)
def show_error_message(message):
    # Implement this function in gui.py to show error messages in the GUI
    pass

def update_progress_bar(value):
    # Implement this function in gui.py to update the progress bar
    pass
