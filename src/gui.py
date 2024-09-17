from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QProgressBar, QVBoxLayout, QWidget, QLabel, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from md_to_pdf import convert_md_to_pdf

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MDtoPDF Converter")
        self.setGeometry(100, 100, 400, 250)  # Increased height to accommodate status label
        self.setStyleSheet("background-color: white;")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        title_label = QLabel("MDtoPDF Converter")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title_label)

        self.convert_button = QPushButton("Choose File")
        self.convert_button.setStyleSheet(
            "background-color: #4CAF50; color: white; border: none; padding: 10px; border-radius: 5px;"
        )
        self.convert_button.clicked.connect(self.convert_file)
        layout.addWidget(self.convert_button, alignment=Qt.AlignCenter)

        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(
            "QProgressBar {border: 2px solid grey; border-radius: 5px; text-align: center;}"
            "QProgressBar::chunk {background-color: #4CAF50; width: 10px;}"
        )
        layout.addWidget(self.progress_bar)

        # Add status label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

    def convert_file(self):
        input_file, _ = QFileDialog.getOpenFileName(self, "Select Markdown File", "", "Markdown Files (*.md)")
        if input_file:
            output_file, _ = QFileDialog.getSaveFileName(self, "Save PDF File", "", "PDF Files (*.pdf)")
            if output_file:
                self.progress_bar.setValue(0)
                self.status_label.setText("Converting...")
                try:
                    convert_md_to_pdf(input_file, output_file, self.update_progress, self.show_error_message)
                    self.progress_bar.setValue(100)
                    self.status_label.setText("Conversion Completed Successfully.")
                    self.show_info_message("Conversion Successful", f"PDF saved to {output_file}")
                except Exception as e:
                    self.show_error_message(str(e))
                    self.progress_bar.setValue(0)
                    self.status_label.setText("Conversion Failed.")

    def update_progress(self, value):
        if value == 100:
            self.status_label.setText("Conversion Completed Successfully.")
        elif value == -1:
            self.status_label.setText("Conversion Failed.")
        else:
            self.progress_bar.setValue(value)
            self.status_label.setText(f"Processing... {value}%")
        
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

# Add more GUI elements and functionality as needed

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
