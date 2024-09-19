# Markdown to PDF Converter

This application converts Markdown files to PDF format with support for emojis, local images, and online images.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/markdown-to-pdf-converter.git
   cd markdown-to-pdf-converter
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the GUI application:
   ```bash
   python src/gui.py
   ```

2. Click "Choose File" to select a Markdown file for conversion.
3. Choose the output location for the PDF file.
4. The application will convert the Markdown to PDF and display the progress.

## Features

- Converts Markdown to PDF
- Supports emojis
- Embeds local images
- Includes images from online sources
- Preserves links in the PDF output

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
