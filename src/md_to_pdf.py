import markdown
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import emoji
import requests
from PIL import Image
import io
import re
import os

def convert_md_to_pdf(input_file, output_file, progress_callback=None):
    with open(input_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert emojis to their Unicode representation
    md_content = emoji.emojize(md_content, language='alias')
    
    # Convert Markdown to HTML
    html_content = markdown.markdown(md_content, extensions=['extra'])
    
    # Process images
    html_content = process_images(html_content, os.path.dirname(input_file))
    
    # Create PDF
    font_config = FontConfiguration()
    html = HTML(string=html_content)
    css = CSS(string='''@font-face { font-family: 'Noto Color Emoji'; src: url('https://github.com/googlefonts/noto-emoji/raw/main/fonts/NotoColorEmoji.ttf'); } body { font-family: Arial, 'Noto Color Emoji', sans-serif; }''', font_config=font_config)
    
    html.write_pdf(output_file, stylesheets=[css], font_config=font_config)
    
    if progress_callback:
        progress_callback(100)

def process_images(html_content, base_path):
    def replace_image(match):
        src = match.group(1)
        if src.startswith(('http://', 'https://')):
            try:
                response = requests.get(src)
                img = Image.open(io.BytesIO(response.content))
            except:
                return match.group(0)  # Return original if fetch fails
        else:
            img_path = os.path.join(base_path, src)
            try:
                img = Image.open(img_path)
            except:
                return match.group(0)  # Return original if file not found
        
        # Process image here if needed (e.g., resize, convert format)
        
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f'<img src="data:image/png;base64,{img_str}" />'

    # Replace both Markdown and HTML image tags
    html_content = re.sub(r'!\[.*?\]\((.*?)\)', replace_image, html_content)
    html_content = re.sub(r'<img.*?src="(.*?)".*?>', replace_image, html_content)
    
    return html_content

# Add more helper functions if needed