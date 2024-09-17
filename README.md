# MDtoPDF

**Support for images and enhanced text formatting.**

## Features

- **Improved Text Readability**: Clear and readable fonts with increased sizes.
- **Enhanced Layout**: Borders around content and support for multiple color schemes.
- **Full Markdown Support**: Accurate rendering of all standard Markdown features.
- **Optimized PDF Output**: Resembles a book format with proper page breaks and a table of contents.

## Getting Started

1. **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/MDtoPDF.git
    ```
2. **Navigate to the Project Directory**
    ```bash
    cd MDtoPDF
    ```
3. **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```
4. **Set Up `wkhtmltopdf`**
    - **Windows**:
        - Download the installer from [wkhtmltopdf Downloads](https://wkhtmltopdf.org/downloads.html).
        - Run the installer and add `wkhtmltopdf` to your system's PATH.
    - **macOS**:
        ```bash
        brew install wkhtmltopdf
        ```
    - **Linux (Ubuntu/Debian)**:
        ```bash
        sudo apt-get update
        sudo apt-get install -y wkhtmltopdf
        ```
5. **Run the Application**
    ```bash
    python src/main.py
    ```

## Project Structure

- `src/`
    - `md_to_pdf.py`: Core functionality for converting Markdown to PDF.
    - `gui.py`: PyQt5-based graphical user interface.
    - `main.py`: Entry point for the application.
- `requirements.txt`: List of Python dependencies.
- `README.md`: Project documentation.
- `LICENSE`: License information.

## Usage

1. **Launch the Application**
    - Run `python src/main.py` from the project directory.
2. **Convert a Markdown File**
    - Click on the "Choose File" button to select a `.md` file.
    - Specify the destination and filename for the generated PDF.
    - Monitor the progress through the progress bar and status messages.

## Features in Detail

### Improved Text Readability

- Utilizes clear and readable fonts similar to GitHub's style.
- Increased font sizes and line spacing enhance visibility and comfort.

### Enhanced Layout

- Adds a subtle border around the PDF content for a polished look.
- Supports multiple color schemes to cater to different preferences.

### Full Markdown Support

- Accurately renders all standard Markdown elements, including headings, lists, code blocks, and more.
- Handles images from both local files and online sources seamlessly.

### Optimized PDF Output

- Structures the PDF to resemble a book format with appropriate page breaks.
- Automatically generates a table of contents for longer documents.

## Troubleshooting

- **wkhtmltopdf Not Found**:
    - Ensure `wkhtmltopdf` is installed and added to your system's PATH.
    - Verify installation by running `wkhtmltopdf --version` in your terminal.
- **Emoji Issues**:
    - Emojis are stripped from the Markdown content to prevent rendering issues.
- **Image Handling**:
    - Ensure that image paths are correct and accessible.
    - For online images, verify your internet connection.

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the Repository**
2. **Create a New Branch**
    ```bash
    git checkout -b feature/YourFeatureName
    ```
3. **Commit Your Changes**
    ```bash
    git commit -m "Add some feature"
    ```
4. **Push to the Branch**
    ```bash
    git push origin feature/YourFeatureName
    ```
5. **Open a Pull Request**

## License

This project is open-source and available under the [MIT License](LICENSE).

---
