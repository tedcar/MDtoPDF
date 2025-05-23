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
import multiprocessing
import psutil
from .styling import get_all_styles, get_page_layout # Updated import
from reportlab.platypus import Frame, PageTemplate # Added for existing code
from reportlab.lib import colors # Added for add_border (though not directly used by create_pdf_with_reportlab styling)

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
            logger.info(f"Successfully converted {input_file} to {output_file} using wkhtmltopdf")
            if progress_callback:
                progress_callback(100)
        else:
            logger.info("wkhtmltopdf not found. Falling back to ReportLab for PDF conversion.")
            if progress_callback:
                progress_callback(50)  # Indicate fallback and partial progress
            
            create_pdf_with_reportlab(html_content, output_file) # Fallback to ReportLab
            
            logger.info(f"Successfully converted {input_file} to {output_file} using ReportLab")
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
        all_styles = get_all_styles()
        default_style = all_styles['Normal']
        
        doc = SimpleDocTemplate(output_file, pagesize=letter, **get_page_layout())
        story = []
    
        soup = BeautifulSoup(html_content, 'html.parser')
        # Updated find_all to include more tags as per plan
        for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'img', 'pre', 'ul', 'ol', 'blockquote', 'hr', 'table']):
            tag_name = element.name

            if tag_name == 'p':
                # Check if the paragraph solely contains an image
                img_children = [child for child in element.children if child.name == 'img']
                # Consider a paragraph to be "image-only" if it has one img child and other children are just whitespace
                non_img_children_significant = [child for child in element.children if child.name != 'img' and str(child).strip()]

                if len(img_children) == 1 and not non_img_children_significant:
                    img_element = img_children[0]
                    img_data = process_image(img_element.get('src'))
                    if img_data:
                        try:
                            img = Image(BytesIO(img_data))
                            img_pil = PILImage.open(BytesIO(img_data))
                            img_width_pil, img_height_pil = img_pil.size
                            aspect = img_height_pil / float(img_width_pil)
                            max_img_width = doc.width
                            img.drawWidth = min(img_width_pil, max_img_width)
                            img.drawHeight = img.drawWidth * aspect
                            story.append(img)
                            story.append(Spacer(1, 12))
                        except Exception as e:
                            logger.error(f"Failed to add image (from p-tag) to PDF: {e}")
                else:
                    # For mixed content paragraphs, parse to remove unsupported img attributes like 'alt'
                    paragraph_html_content = element.decode_contents()
                    temp_soup = BeautifulSoup(paragraph_html_content, 'html.parser')
                    for img_tag in temp_soup.find_all('img'):
                        if img_tag.get('src', '').startswith(('http://', 'https://')):
                            # ReportLab's Paragraph does not fetch remote images.
                            # Replace with placeholder text or modify src to a downloaded version if implemented.
                            # For now, replace the img tag with a text placeholder to prevent error.
                            original_src = img_tag['src']
                            placeholder_text = f"[Remote Image: {original_src} placeholder]"
                            # Create a new text node from the placeholder_text
                            # We need to use the new_string method of the *original* soup object that created the tag
                            # or a new soup object if we are replacing within a string context.
                            # Since temp_soup is its own parsed object, we can use its new_string.
                            img_tag.replace_with(temp_soup.new_string(placeholder_text))
                            logger.info(f"Replaced remote image '{original_src}' in paragraph with placeholder text.")
                        else: # For local images, just ensure problematic attributes are removed
                            if 'alt' in img_tag.attrs:
                                del img_tag['alt']
                            if 'style' in img_tag.attrs:
                                del img_tag['style']
                    
                    story.append(Paragraph(str(temp_soup), all_styles.get('Normal', default_style)))
                    story.append(Spacer(1, 6)) # Reduced spacer after paragraphs
            elif tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                style_name = tag_name.upper() # H1, H2, H3
                if style_name not in ['H1', 'H2', 'H3']: # Fallback for H4-H6
                    style_name = 'H3' 
                style = all_styles.get(style_name, default_style)
                story.append(Paragraph(element.decode_contents(), style))
                story.append(Spacer(1, style.spaceBefore / 2 if hasattr(style, 'spaceBefore') else 6)) # Spacer based on style
                if tag_name == 'h1':
                    story.append(PageBreak())
            elif tag_name == 'img':
                img_data = process_image(element['src'])
                if img_data: # This is for direct img tags, not img within p
                    try:
                        img = Image(BytesIO(img_data))
                        img_pil = PILImage.open(BytesIO(img_data))
                        img_width_pil, img_height_pil = img_pil.size
                        aspect = img_height_pil / float(img_width_pil)
                        max_img_width = doc.width
                        img.drawWidth = min(img_width_pil, max_img_width)
                        img.drawHeight = img.drawWidth * aspect
                        story.append(img)
                        story.append(Spacer(1, 12))
                    except Exception as e:
                        logger.error(f"Failed to add direct image to PDF: {e}")
            elif tag_name == 'pre':
                code_element = element.find('code')
                text = code_element.get_text(strip=True) if code_element else element.get_text(strip=True)
                story.append(Paragraph(text, all_styles.get('Code', default_style)))
                story.append(Spacer(1, 12))
            elif tag_name == 'ul':
                for li in element.find_all('li', recursive=False):
                    bullet_text = f"• {li.decode_contents()}"
                    story.append(Paragraph(bullet_text, all_styles.get('Bullet', default_style)))
                    story.append(Spacer(1, 2)) # Tighter spacing for list items
                story.append(Spacer(1, 6)) # Space after list
            elif tag_name == 'ol':
                ol_counter = 1
                for li in element.find_all('li', recursive=False):
                    numbered_text = f"{ol_counter}. {li.decode_contents()}"
                    story.append(Paragraph(numbered_text, all_styles.get('ListItem', default_style)))
                    story.append(Spacer(1, 2)) # Tighter spacing for list items
                    ol_counter += 1
                story.append(Spacer(1, 6)) # Space after list
            elif tag_name == 'blockquote':
                # Process each paragraph within the blockquote
                inner_paragraphs = element.find_all('p')
                if inner_paragraphs:
                    for p_element in inner_paragraphs:
                        story.append(Paragraph(p_element.decode_contents(), all_styles.get('Blockquote', default_style)))
                        story.append(Spacer(1, 3)) 
                else: # If no <p> tags, process the whole content
                    story.append(Paragraph(element.decode_contents(), all_styles.get('Blockquote', default_style)))
                story.append(Spacer(1, 6))
            elif tag_name == 'hr':
                story.append(Spacer(1, 24)) # Use a larger spacer for hr
            elif tag_name == 'table':
                logger.warning("HTML tables are not supported in ReportLab PDF conversion and will be skipped.")
                # Optionally, add a placeholder paragraph:
                # story.append(Paragraph("[Table content skipped]", default_style))
                # story.append(Spacer(1, 12))

        # The Frame and PageTemplate part for borders - keep as is for now
        # This might need adjustment if 'add_border' or related functionality is broken
        # or if these ReportLab components are not correctly imported/defined.
        # For now, the focus is on content styling.
        # Ensure 'Frame' and 'PageTemplate' are imported if this part is to be kept.
        # It seems `add_border` is defined below and uses `colors` which needs to be imported.
        # `Frame` and `PageTemplate` are not standard Python types, they come from ReportLab.
        
        # Example of how it was:
        # frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
        # template = PageTemplate(id='with_border', frames=[frame], onPage=add_border)
        # doc.addPageTemplates([template])
        # This part is kept from the original, assuming Frame, PageTemplate, add_border are available.
        # If `add_border` is not defined or `Frame`/`PageTemplate` are not imported, this will error.
        # The current task is styling, so this structure is maintained.
        # `add_border` itself is defined later in the file.
        # `Frame` and `PageTemplate` are typically imported from `reportlab.platypus`.
        # `colors` is typically imported from `reportlab.lib.colors`.

        # The following lines for frame and template are from the original code.
        # If `add_border` is not used or `Frame`/`PageTemplate` are not properly imported,
        # these could be removed or commented out.
        # For now, retaining them as the subtask is about style application.
        if 'Frame' in globals() and 'PageTemplate' in globals() and callable(globals().get('add_border')):
             frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
             template = PageTemplate(id='with_border', frames=[frame], onPage=add_border)
             doc.addPageTemplates([template])
        else:
             logger.warning("Frame, PageTemplate, or add_border not fully available. Skipping page border.")

        doc.build(story)
        logger.info("ReportLab PDF creation succeeded.")
    except KeyError as ke:
        missing_style = ke.args[0].split("'")[1]
        logger.error(f"Style '{missing_style}' not found in stylesheet.")
        raise # Re-raise the KeyError
    except Exception as e:
        logger.error(f"Error creating PDF with ReportLab: {e}")
        raise # Re-raise the exception

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
