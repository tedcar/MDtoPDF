import os
import logging
from unittest import mock
import sys

# Add the project root directory (parent of 'src') to sys.path
# This allows Python to find the 'src' package
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

# Now import modules from the 'src' package
try:
    from src import md_to_pdf
    print("Successfully imported md_to_pdf from src package.")
except ImportError as e:
    print(f"Error importing from src package: {e}")
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred during import: {e}") # Catch any other import error
    sys.exit(1)


# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Define input and output files
input_md = "MDtoPDF.md" # Assumes script is run from project root
output_pdf = "test_output_reportlab.pdf" # Output in project root

# Check if input file exists
if not os.path.exists(input_md):
    logger.error(f"Input file {input_md} not found. Make sure it's in the project root directory.")
    sys.exit(1)

# Check if TimesNewRoman.ttf exists in src, as styling.py depends on it.
font_check_path = os.path.join(project_root, "src", "TimesNewRoman.ttf")
if not os.path.exists(font_check_path):
    logger.warning(f"Font file {font_check_path} not found. Styling might be affected.")


@mock.patch('src.md_to_pdf.get_wkhtmltopdf_path', return_value=None)
def run_conversion_test(mock_get_path):
    logger.info(f"Attempting to convert {input_md} to {output_pdf} using ReportLab...")
    try:
        # Call the function from the imported module
        md_to_pdf.convert_md_to_pdf(input_md, output_pdf)
        logger.info("Conversion process completed.")
        
        # Verify mock was called
        mock_get_path.assert_called_once()
        logger.info("Mock for get_wkhtmltopdf_path was called, ensuring ReportLab path was intended.")
        
        if os.path.exists(output_pdf):
            logger.info(f"Output file {output_pdf} created successfully.")
            logger.info(f"File size: {os.path.getsize(output_pdf)} bytes.")
        else:
            logger.error(f"Output file {output_pdf} was NOT created.")
            
    except Exception as e:
        logger.error(f"An error occurred during conversion: {e}", exc_info=True)

if __name__ == "__main__":
    print(f"Current working directory: {os.getcwd()}")
    print(f"Sys path: {sys.path}")
    # Ensure the script is run from the project root for correct path handling
    expected_cwd = project_root
    if os.getcwd() != expected_cwd:
        logger.warning(f"Script is being run from {os.getcwd()} instead of {expected_cwd}. Path issues might occur.")
        # os.chdir(expected_cwd) # Optionally change to expected CWD

    print("Running conversion test...")
    run_conversion_test()
    print("Test script finished.")
