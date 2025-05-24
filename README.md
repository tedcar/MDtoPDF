# Markdown to PDF Converter

A simple application to convert your Markdown files into PDF documents. Supports emojis, local images, and online images, with good styling for PDF output.

## Features

*   Converts Markdown files to PDF.
*   Handles emojis (by stripping them, ensuring clean output).
*   Embeds local and online images.
*   Preserves hyperlinks from your Markdown.
*   Uses `wkhtmltopdf` if available for high-fidelity PDF generation, with a fallback to ReportLab for good-quality PDFs even without `wkhtmltopdf`.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Prerequisites

*   Python 3.7+
*   `pip` (Python package installer)
*   Optional, but recommended for best PDF quality: `wkhtmltopdf`.
    *   Download from [wkhtmltopdf.org](https://wkhtmltopdf.org/downloads.html) and ensure it's added to your system's PATH or set the `WKHTMLTOPDF_PATH` environment variable.

### Installation & Running

1.  **Clone the repository:**
    ```bash
    git clone <repository_url> 
    # Replace <repository_url> with the actual URL of this repository
    cd markdown-to-pdf-converter
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    ```
    *   On Windows: `venv\Scripts\activate`
    *   On macOS/Linux: `source venv/bin/activate`

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    ```bash
    python src/main.py
    ```
    This will launch the graphical user interface. Click "Choose File" to select your Markdown file and specify the output PDF location.

## Packaging (Optional)

While this application is designed to be run from source, it can be packaged into a standalone executable using [PyInstaller](https://pyinstaller.org/en/stable/). You would typically need to install PyInstaller and then run a command similar to:
`pyinstaller --name MDtoPDFConverter --onefile --windowed --add-data "src/TimesNewRoman.ttf:." src/main.py`
Ensure `TimesNewRoman.ttf` is correctly bundled and that `src/utils.py`'s `resource_path` function is used to locate it. Refer to PyInstaller documentation for more details on handling data files and other options.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License. (A `LICENSE` file should ideally be present in the repository).
