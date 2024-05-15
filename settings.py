# settings.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, \
    QListWidgetItem, QMessageBox, QInputDialog
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from models import Topic, Pomodoro, get_session, get_engine


class SettingsDialog(QDialog):
    topic_added = pyqtSignal()  # Yeni sinyal tanımlandı

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ayarlar")
        self.setGeometry(200, 200, 400, 300)
        self.engine = get_engine()
        self.session = get_session(self.engine)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        label_font = QFont('Arial', 14, QFont.Bold)
        input_font = QFont('Arial', 12)

        # Konu Girişi
        topic_layout = QHBoxLayout()
        self.topic_label = QLabel("Yeni Konu:")
        self.topic_label.setFont(label_font)
        self.topic_input = QLineEdit()
        self.topic_input.setFont(input_font)
        self.topic_add_button = QPushButton("Konu Ekle")
        self.topic_add_button.setFont(input_font)
        self.topic_add_button.clicked.connect(self.add_topic)

        topic_layout.addWidget(self.topic_label)
        topic_layout.addWidget(self.topic_input)
        topic_layout.addWidget(self.topic_add_button)

        # Konu Listesi
        self.topic_list = QListWidget()
        self.topic_list.setFont(input_font)
        self.topic_list.itemDoubleClicked.connect(self.edit_topic)  # Çift tıklama ile düzenleme
        self.load_topics()

        # Tüm Verileri Sil Butonu
        self.delete_all_button = QPushButton("Tüm Verileri Sil")
        self.delete_all_button.setFont(label_font)
        self.delete_all_button.setStyleSheet("color: red;")
        self.delete_all_button.clicked.connect(self.delete_all_data)

        layout.addLayout(topic_layout)
        layout.addWidget(self.topic_list)
        layout.addWidget(self.delete_all_button)

        self.setLayout(layout)

    def load_topics(self):
        self.topic_list.clear()
        topics = self.session.query(Topic).all()
        for topic in topics:
            item = QListWidgetItem(topic.name)
            item.setData(Qt.UserRole, topic.id)
            self.topic_list.addItem(item)

    def add_topic(self):
        topic_name = self.topic_input.text().strip()
        if topic_name:
            if not self.session.query(Topic).filter_by(name=topic_name).first():
                new_topic = Topic(name=topic_name)
                self.session.add(new_topic)
                self.session.commit()
                self.topic_input.clear()
                self.load_topics()
                self.topic_added.emit()  # Yeni konu eklendiğinde sinyal gönderildi
                QMessageBox.information(self, "Başarılı", f"Konu '{topic_name}' başarıyla eklendi.")
            else:
                QMessageBox.warning(self, "Uyarı", f"Konu '{topic_name}' zaten mevcut.")
        else:
            QMessageBox.warning(self, "Uyarı", "Konu adı boş olamaz.")

    def edit_topic(self, item):
        topic_id = item.data(Qt.UserRole)
        topic = self.session.query(Topic).filter_by(id=topic_id).first()

        if topic:
            new_name, ok = QInputDialog.getText(self, "Konuyu Düzenle", "Yeni adı girin:", QLineEdit.Normal, topic.name)
            if ok and new_name:
                if not self.session.query(Topic).filter_by(name=new_name).first():
                    topic.name = new_name
                    self.session.commit()
                    self.load_topics()
                    self.topic_added.emit()  # Konu düzenlendiğinde sinyal gönderildi
                    QMessageBox.information(self, "Başarılı", f"Konu '{new_name}' başarıyla güncellendi.")
                else:
                    QMessageBox.warning(self, "Uyarı", f"Konu '{new_name}' zaten mevcut.")

    def delete_all_data(self):
        reply = QMessageBox.warning(self, "Dikkat",
                                    "Tüm verileri silmek üzeresiniz. Bu işlem geri alınamaz!\nDevam etmek istediğinizden emin misiniz?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                self.session.query(Pomodoro).delete()
                self.session.query(Topic).delete()
                self.session.commit()
                self.load_topics()
                self.topic_added.emit()  # Veriler silindiğinde sinyal gönderildi
                QMessageBox.information(self, "Başarılı", "Tüm veriler başarıyla silindi.")
            except Exception as e:
                self.session.rollback()
                QMessageBox.critical(self, "Hata", f"Veriler silinirken bir hata oluştu: {e}")
