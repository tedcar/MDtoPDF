from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QFileDialog, 
                             QProgressBar, QVBoxLayout, QWidget, QLabel, QMessageBox)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from md_to_pdf import convert_md_to_pdf
import os

class ConversionThread(QThread):
    progress_update = pyqtSignal(int)
    conversion_complete = pyqtSignal()
    conversion_error = pyqtSignal(str)

    def __init__(self, input_file, output_file):
        super().__init__()
        self.input_file = input_file
        self.output_file = output_file

    def run(self):
        try:
            convert_md_to_pdf(self.input_file, self.output_file, 
                              lambda value: self.progress_update.emit(value))
            self.conversion_complete.emit()
        except Exception as e:
            self.conversion_error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MDtoPDF Converter")
        self.setGeometry(100, 100, 600, 400)  # Increased size
        self.setStyleSheet("background-color: white;")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        title_label = QLabel("MDtoPDF Converter")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 24, QFont.Bold))  # Increased font size
        layout.addWidget(title_label)

        self.convert_button = QPushButton("Choose File")
        self.convert_button.setStyleSheet(
            "background-color: #4CAF50; color: white; border: none; padding: 15px; border-radius: 8px; font-size: 18px;"
        )
        self.convert_button.clicked.connect(self.convert_file)
        layout.addWidget(self.convert_button, alignment=Qt.AlignCenter)

        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(
            "QProgressBar {border: 2px solid grey; border-radius: 5px; text-align: center; height: 30px;}"
            "QProgressBar::chunk {background-color: #4CAF50; width: 20px;}"
        )
        layout.addWidget(self.progress_bar)

        # Add status label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Arial", 16))  # Increased font size
        layout.addWidget(self.status_label)

    def convert_file(self):
        input_file, _ = QFileDialog.getOpenFileName(self, "Select Markdown File", "", "Markdown Files (*.md)")
        if input_file:
            output_file, _ = QFileDialog.getSaveFileName(self, "Save PDF File", "", "PDF Files (*.pdf)")
            if output_file:
                self.progress_bar.setValue(0)
                self.status_label.setText("Converting...")
                self.thread = ConversionThread(input_file, output_file)
                self.thread.progress_update.connect(self.update_progress)
                self.thread.conversion_complete.connect(self.conversion_complete)
                self.thread.conversion_error.connect(self.conversion_error)
                self.thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)
        self.status_label.setText(f"Processing... {value}%")

    def conversion_complete(self):
        self.progress_bar.setValue(100)
        self.status_label.setText("Conversion Completed Successfully.")
        self.show_info_message("Conversion Successful", "PDF saved successfully.")

    def conversion_error(self, error):
        self.progress_bar.setValue(0)
        self.status_label.setText("Conversion Failed.")
        self.show_error_message(error)

    def show_error_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Conversion Error")
        msg.setInformativeText(message)
        msg.setWindowTitle("Error")
        msg.exec_()

    def show_info_message(self, title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.exec_()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
