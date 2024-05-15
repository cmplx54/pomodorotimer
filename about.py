# about.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import os

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hakkında")
        self.setGeometry(300, 300, 400, 300)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Metin dosyasını oku
        text = self.load_text()

        # Metin içeriği
        about_label = QLabel(text)
        about_label.setFont(QFont('Arial', 16))
        about_label.setAlignment(Qt.AlignCenter)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(about_label)
        hbox.addStretch(1)

        layout.addLayout(hbox)

        self.setLayout(layout)

    def load_text(self):
        file_path = os.path.join(os.path.dirname(__file__), 'metin.txt')
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            return f"Metin dosyası okunamadı: {e}"
