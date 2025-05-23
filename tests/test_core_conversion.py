import unittest
from unittest import mock
import os
import sys
import tempfile
import shutil
import logging

# Add project root to sys.path to allow importing from src
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

try:
    from src.md_to_pdf import convert_md_to_pdf, get_wkhtmltopdf_path
except ImportError as e:
    logging.error(f"Failed to import from src.md_to_pdf: {e}")
    # This is a fallback for environments where src might not be seen as a package easily
    # It assumes the script might be run with CWD set to src or similar.
    # For robust testing, ensuring the correct PYTHONPATH or running as a module is better.
    if 'src.md_to_pdf' not in str(e): # Avoid recursion if the error is different
        from md_to_pdf import convert_md_to_pdf, get_wkhtmltopdf_path


# Configure basic logging for tests (optional, but can be helpful)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TestCoreConversion(unittest.TestCase):

    def setUp(self):
        """Create a temporary directory for PDF outputs."""
        self.temp_dir = tempfile.mkdtemp()
        logger.debug(f"Temporary directory created: {self.temp_dir}")

    def tearDown(self):
        """Remove the temporary directory and its contents."""
        shutil.rmtree(self.temp_dir)
        logger.debug(f"Temporary directory removed: {self.temp_dir}")

    def _run_conversion_test(self, md_file_name, output_pdf_name, mock_wkhtmltopdf_path_return):
        """
        Helper method to run a conversion test.
        Mocks get_wkhtmltopdf_path to control which conversion path is taken.
        """
        md_file_path = os.path.join(project_root, "tests", "test_assets", md_file_name)
        output_pdf_path = os.path.join(self.temp_dir, output_pdf_name)

        self.assertTrue(os.path.exists(md_file_path), f"Test Markdown file not found: {md_file_path}")

        # Use a new mock object for each call to _run_conversion_test
        # The target of the mock is 'src.md_to_pdf.get_wkhtmltopdf_path'
        # because convert_md_to_pdf in src.md_to_pdf imports it that way.
        with mock.patch('src.md_to_pdf.get_wkhtmltopdf_path') as mock_get_path:
            mock_get_path.return_value = mock_wkhtmltopdf_path_return
            
            logger.info(f"Running conversion for {md_file_path} -> {output_pdf_path} (wkhtmltopdf_path mock: {mock_wkhtmltopdf_path_return})")
            
            try:
                convert_md_to_pdf(md_file_path, output_pdf_path)
            except OSError as e:
                if "No wkhtmltopdf executable found" in str(e) and mock_wkhtmltopdf_path_return is not None:
                    self.skipTest(f"wkhtmltopdf not installed or found at '{mock_wkhtmltopdf_path_return}', skipping pdfkit path test.")
                else:
                    self.fail(f"convert_md_to_pdf raised an OSError: {e}\n"
                              f"MD File: {md_file_path}, Output: {output_pdf_path}, Mock Return: {mock_wkhtmltopdf_path_return}")
            except Exception as e:
                self.fail(f"convert_md_to_pdf raised an unexpected exception: {e}\n"
                          f"MD File: {md_file_path}, Output: {output_pdf_path}, Mock Return: {mock_wkhtmltopdf_path_return}")

            # This assertion will only be reached if the conversion didn't raise an unskipped error
            if not (mock_wkhtmltopdf_path_return is not None and "No wkhtmltopdf executable found" in str(getattr(self, '_outcome', {}).result.skipped if hasattr(self, '_outcome') and hasattr(self._outcome, 'result') and self._outcome.result else "")): # Check if test was skipped
                 self.assertTrue(os.path.exists(output_pdf_path), 
                                 f"Output PDF file was not created: {output_pdf_path}")
            if not (mock_wkhtmltopdf_path_return is not None and "No wkhtmltopdf executable found" in str(getattr(self, '_outcome', {}).result.skipped if hasattr(self, '_outcome') and hasattr(self._outcome, 'result') and self._outcome.result else "")): # Check if test was skipped
                 self.assertTrue(os.path.getsize(output_pdf_path) > 0, 
                                 f"Output PDF file is empty: {output_pdf_path}")
            mock_get_path.assert_called_once() # This should always be called
            logger.info(f"Conversion attempt finished for {output_pdf_name}")


    # --- Tests for basic.md ---
    def test_basic_md_pdfkit(self):
        self._run_conversion_test('basic.md', 'basic_pdfkit.pdf', mock_wkhtmltopdf_path_return='/usr/bin/wkhtmltopdf')

    def test_basic_md_reportlab(self):
        self._run_conversion_test('basic.md', 'basic_reportlab.pdf', mock_wkhtmltopdf_path_return=None)

    # --- Tests for lists_code.md ---
    def test_lists_code_md_pdfkit(self):
        self._run_conversion_test('lists_code.md', 'lists_code_pdfkit.pdf', mock_wkhtmltopdf_path_return='/usr/bin/wkhtmltopdf')

    def test_lists_code_md_reportlab(self):
        self._run_conversion_test('lists_code.md', 'lists_code_reportlab.pdf', mock_wkhtmltopdf_path_return=None)

    # --- Tests for image_link.md ---
    def test_image_link_md_pdfkit(self):
        # Assuming wkhtmltopdf can handle online images if network is available
        self._run_conversion_test('image_link.md', 'image_link_pdfkit.pdf', mock_wkhtmltopdf_path_return='/usr/bin/wkhtmltopdf')

    def test_image_link_md_reportlab(self):
        # ReportLab path also attempts to fetch online images.
        # Test ensures PDF creation even if image fetching fails (logged by app).
        self._run_conversion_test('image_link.md', 'image_link_reportlab.pdf', mock_wkhtmltopdf_path_return=None)


if __name__ == '__main__':
    # This allows running the tests directly from the command line
    # Ensure that the environment is set up for src imports if run this way.
    # Example: PYTHONPATH=$PYTHONPATH:/path/to/your/project/root python tests/test_core_conversion.py
    logger.info("Running TestCoreConversion directly.")
    unittest.main()
