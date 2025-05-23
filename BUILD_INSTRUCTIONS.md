# How to Build a Windows Executable for MDtoPDFConverter

This document provides instructions on how to build a single-file Windows executable (`.exe`) for the MDtoPDFConverter application using PyInstaller.

## 1. Prerequisites

Before you begin, ensure you have the following installed:

*   **Python:** Make sure Python is installed and configured in your system's PATH.
*   **Required Python Packages:** Install all necessary dependencies using pip:
    ```bash
    pip install pyinstaller pyqt5 reportlab markdown beautifulsoup4 pdfkit psutil
    ```
    *(Note: `pdfkit` is listed as it's part of the project, though its primary dependency `wkhtmltopdf` is handled separately).*

## 2. Modifying Code to Handle Bundled Data Files

When PyInstaller bundles an application, data files like fonts are stored in a temporary location. The application needs a way to find these files at runtime.

### The `resource_path` Helper Function

You need to use a helper function to get the correct path to bundled resources. Create or ensure the following function is available, for example, in your `src/main.py` or a utility module that can be imported by `src/styling.py`:

```python
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # sys._MEIPASS is not defined, so running in development
        # Assuming the script is in 'src' and 'TimesNewRoman.ttf' is also in 'src'
        # or relative_path is relative to the project root if run from there.
        # For styling.py in src, and font in src:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__))) # if this function is in src
        # If this function is in project root, and you call resource_path('src/TimesNewRoman.ttf')
        # base_path = os.path.abspath(".") 
    
    return os.path.join(base_path, relative_path)
```

### Update `src/styling.py`

The `src/styling.py` file needs to be modified to use `resource_path` to load `TimesNewRoman.ttf`.

Assuming `resource_path` is defined in a way that's importable into `styling.py` (e.g., if `resource_path` is in `main.py`, you might need to adjust imports or move `resource_path` to a utility file in `src`), change the font loading part in `src/styling.py`:

**Original (example):**
```python
# font_path = os.path.join(os.path.dirname(__file__), 'TimesNewRoman.ttf') 
# pdfmetrics.registerFont(TTFont('TimesNewRoman', font_path))
```

**Modified (example):**
```python
# Assuming resource_path is imported, e.g., from main or a utility module
# from .main import resource_path # Or wherever it's defined

# Path to the font file. When bundled, it will be in the root of _MEIPASS.
font_file = 'TimesNewRoman.ttf' 
font_path_in_bundle = resource_path(font_file) # This will point to _MEIPASS/TimesNewRoman.ttf

# Fallback for development if resource_path is structured for _MEIPASS primarily
# and you are running styling.py directly for tests (not typical for this app structure)
if not os.path.exists(font_path_in_bundle) and not hasattr(sys, '_MEIPASS'):
    # Dev mode: if resource_path points to project root, and font is in src
    # font_path_in_bundle = os.path.join(os.path.dirname(__file__), font_file)
    # Simpler: if resource_path is in styling.py itself or a util in src:
    font_path_in_bundle = os.path.join(os.path.dirname(__file__), font_file)


if os.path.exists(font_path_in_bundle):
    pdfmetrics.registerFont(TTFont('TimesNewRoman', font_path_in_bundle))
    times_new_roman_registered = True
    print(f"Successfully registered font: TimesNewRoman from {font_path_in_bundle}")
else:
    print(f"Warning: Font {font_path_in_bundle} not found. ReportLab may use a default font.")
    times_new_roman_registered = False

# The get_base_style() would then use times_new_roman_registered as before.
```
*Self-correction: The `resource_path` function as provided in the prompt is fine. The key is how `base_path` is determined in development mode. If `styling.py` calls `resource_path('TimesNewRoman.ttf')`, and `resource_path` is in `styling.py`, then `os.path.abspath(".")` inside `resource_path` would be `src/`. So `os.path.join(base_path, relative_path)` would correctly become `src/TimesNewRoman.ttf` in dev mode if `styling.py` is in `src`.*

*The `resource_path` function as provided in the prompt is standard. The critical change in `styling.py` is:*
```python
# Assuming resource_path is imported or defined in styling.py itself
# (If defined elsewhere, adjust import: from .utils import resource_path)

font_filename = 'TimesNewRoman.ttf' # The name of the font file in the bundle root
actual_font_path = resource_path(font_filename)

times_new_roman_registered = False
if os.path.exists(actual_font_path):
    try:
        pdfmetrics.registerFont(TTFont('TimesNewRoman', actual_font_path))
        times_new_roman_registered = True
        print(f"Successfully registered font: TimesNewRoman from {actual_font_path}")
    except Exception as e:
        print(f"Error registering TimesNewRoman from {actual_font_path}: {e}")
else:
    # This case should ideally not happen if --add-data is correct and resource_path works
    print(f"Warning: Font {actual_font_path} not found after using resource_path. Check PyInstaller bundling and resource_path logic.")

# ... rest of the styling.py, ensuring get_base_style uses times_new_roman_registered ...
```

## 3. Building the Executable

Open your terminal or command prompt, navigate to the **root directory** of the MDtoPDFConverter project (the directory containing `src/` and `MDtoPDF.md`), and run the following PyInstaller command:

```bash
pyinstaller --name MDtoPDFConverter ^
    --onefile ^
    --windowed ^
    --add-data "src/TimesNewRoman.ttf:." ^
    --icon="path/to/your/icon.ico" ^
    src/main.py
```

**Explanation of the command options:**

*   `pyinstaller`: The command to run PyInstaller.
*   `--name MDtoPDFConverter`: Sets the name of your executable and `.spec` file.
*   `--onefile`: Creates a single executable file. Without this, PyInstaller creates a folder with many files.
*   `--windowed`: Prevents a console window from appearing when the GUI application is run. Use `--console` or remove this for debugging.
*   `--add-data "src/TimesNewRoman.ttf:."`: Bundles the `TimesNewRoman.ttf` font file.
    *   `src/TimesNewRoman.ttf` is the path to your font file (relative to where you run the PyInstaller command).
    *   `:.` means the font file will be placed in the root of the bundled application's temporary directory (`sys._MEIPASS` at runtime). This is why `resource_path('TimesNewRoman.ttf')` is used in the code.
*   `--icon="path/to/your/icon.ico"`: (Optional) Specifies an icon file (`.ico` on Windows) to be used for the executable. Replace `path/to/your/icon.ico` with the actual path to your icon file.
*   `src/main.py`: This is the main script (entry point) of your application.

*(Note: For Linux/macOS, the path separator in `--add-data` is `:`, e.g., `"src/TimesNewRoman.ttf:."`. The `^` is for Windows line continuation; use `\` on Linux/macOS or write the command on a single line.)*

### Using a `.spec` File (Recommended for Complex Projects)

For more control, PyInstaller uses a `.spec` file. You can generate one by running PyInstaller with your options once (without `--onefile` first can be easier to debug):

```bash
pyinstaller --name MDtoPDFConverter --windowed --add-data "src/TimesNewRoman.ttf:." src/main.py
```

This creates `MDtoPDFConverter.spec`. You can then edit this file to add more complex configurations (e.g., hidden imports, more data files, etc.). After editing, you build using the `.spec` file:

```bash
pyinstaller MDtoPDFConverter.spec --onefile
```
*(You'd typically add `--onefile` to the `pyinstaller` command that uses the spec file, or ensure the spec file options lead to a one-file build if that's the final goal).*

## 4. Locating the Executable

After the build process completes, you will find the executable in a folder named `dist` within your project root directory. For the one-file build, it will be `dist/MDtoPDFConverter.exe`.

## 5. Potential Issues and Notes

*   **Hidden Imports:** PyQt5 can sometimes have hidden imports that PyInstaller doesn't automatically detect. If you encounter `ImportError` issues at runtime, you might need to add `--hidden-import=PyQt5.sip` or other relevant PyQt5 modules to the PyInstaller command or edit the `.spec` file. Common ones include `PyQt5.QtCore`, `PyQt5.QtGui`, `PyQt5.QtWidgets`.
*   **`wkhtmltopdf` Not Bundled:** This application uses `wkhtmltopdf` for its primary PDF conversion method if available. `wkhtmltopdf` is an external program and **is not bundled** by PyInstaller with this command.
    *   For the `.exe` to use `wkhtmltopdf`, it must be installed on the target system.
    *   The application's `get_wkhtmltopdf_path()` function attempts to find it in common locations and via the `WKHTMLTOPDF_PATH` environment variable. Users of the `.exe` might need to set this environment variable if `wkhtmltopdf` is installed in a non-standard location.
    *   If `wkhtmltopdf` is not found, the application will fall back to using ReportLab for PDF conversion, which *is* bundled with the executable.
*   **Console Window for Debugging:** If the application fails to start, try building without `--windowed` (i.e., with `--console`) to see error messages in a command prompt.
*   **Permissions:** Ensure you have the necessary permissions to write to the build and dist folders.
*   **Antivirus Software:** Antivirus software can sometimes flag PyInstaller-generated executables as suspicious (false positives). This is a known issue.
*   **Large File Size:** `--onefile` executables can be larger as they bundle everything. They also have a slightly slower startup time as files are extracted to a temporary location.

This guide provides a starting point. Complex applications might require further adjustments to the PyInstaller configuration. Always test the executable on a clean machine (or VM) that doesn't have your development environment set up.
```
