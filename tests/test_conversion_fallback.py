import unittest
from unittest import mock
import os
import tempfile
import shutil
import logging
import sys

# Add the project root to sys.path to allow importing from src
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.md_to_pdf import convert_md_to_pdf

class TestConversionFallback(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for PDF output
        self.temp_dir = tempfile.mkdtemp()
        self.output_pdf_path = os.path.join(self.temp_dir, "output.pdf")
        
        # Define the path to the input Markdown file in test_assets
        self.input_md_path = os.path.join(project_root, "tests", "test_assets", "simple_test.md")

        # Ensure the input MD file exists
        if not os.path.exists(self.input_md_path):
            self.fail(f"Test input file not found: {self.input_md_path}")

    def tearDown(self):
        # Remove the temporary directory and its contents
        shutil.rmtree(self.temp_dir)

    @mock.patch('src.md_to_pdf.get_wkhtmltopdf_path', return_value=None)
    def test_reportlab_fallback(self, mock_get_wkhtmltopdf_path):
        """
        Test that convert_md_to_pdf falls back to ReportLab when wkhtmltopdf is not found.
        """
        # Configure logging to capture messages from src.md_to_pdf
        logger = logging.getLogger('src.md_to_pdf')
        
        with self.assertLogs(logger, level='INFO') as cm:
            convert_md_to_pdf(self.input_md_path, self.output_pdf_path)
        
        # Assert that the output PDF file was created
        self.assertTrue(os.path.exists(self.output_pdf_path), "Output PDF file was not created.")
        
        # Assert that the output PDF file is not empty
        self.assertTrue(os.path.getsize(self.output_pdf_path) > 0, "Output PDF file is empty.")
        
        # Assert that the fallback log message was emitted
        self.assertTrue(
            any("Falling back to ReportLab for PDF conversion." in message for message in cm.output),
            "Log message indicating ReportLab fallback was not found."
        )
        
        # Assert that wkhtmltopdf_path was actually called (to ensure mock worked)
        mock_get_wkhtmltopdf_path.assert_called_once()

if __name__ == '__main__':
    unittest.main()
