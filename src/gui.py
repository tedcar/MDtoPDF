from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QProgressBar
from md_to_pdf import convert_md_to_pdf

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MDtoPDF Converter")
        self.setGeometry(100, 100, 300, 200)

        self.convert_button = QPushButton("Convert MD to PDF", self)
        self.convert_button.setGeometry(50, 50, 200, 30)
        self.convert_button.clicked.connect(self.convert_file)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(50, 100, 200, 30)
        self.progress_bar.setValue(0)

    def convert_file(self):
        input_file, _ = QFileDialog.getOpenFileName(self, "Select Markdown File", "", "Markdown Files (*.md)")
        if input_file:
            output_file, _ = QFileDialog.getSaveFileName(self, "Save PDF File", "", "PDF Files (*.pdf)")
            if output_file:
                convert_md_to_pdf(input_file, output_file)
                self.progress_bar.setValue(100)

# Add more GUI elements and functionality
