# history.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, \
    QHeaderView, QMessageBox, QDateEdit, QComboBox
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from models import get_session, get_engine, Pomodoro, Topic
import datetime
import pytz


class HistoryDialog(QDialog):
    pomodoro_deleted = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Geçmiş Pomodorolar")
        self.setGeometry(200, 200, 800, 600)
        self.engine = get_engine()
        self.session = get_session(self.engine)
        self.initUI()

    def get_local_time(self):
        local_tz = pytz.timezone('Europe/Istanbul')  # Yerel zaman diliminizi burada ayarlayın
        return datetime.datetime.now(local_tz)

    def initUI(self):
        layout = QVBoxLayout()

        # Tarih Aralığı Seçimi
        self.start_date_edit = QDateEdit(calendarPopup=True)
        self.end_date_edit = QDateEdit(calendarPopup=True)
        self.set_default_week_dates()  # Default tarih aralığı olarak bu haftayı ayarla
        self.date_range_button = QPushButton("Pomodoroları Göster")
        self.date_range_button.clicked.connect(self.load_pomodoros)

        date_range_layout = QHBoxLayout()
        date_range_layout.addWidget(QLabel("Başlangıç Tarihi:"))
        date_range_layout.addWidget(self.start_date_edit)
        date_range_layout.addWidget(QLabel("Bitiş Tarihi:"))
        date_range_layout.addWidget(self.end_date_edit)
        date_range_layout.addWidget(self.date_range_button)

        # Konu Seçimi
        self.topic_combobox = QComboBox()
        self.load_topics()
        self.topic_combobox.currentTextChanged.connect(self.load_pomodoros)  # Konu değiştiğinde pomodoroları güncelle

        topic_layout = QHBoxLayout()
        topic_layout.addWidget(QLabel("Konu:"))
        topic_layout.addWidget(self.topic_combobox)

        # Pomodoro Tablosu
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Tarih", "Süre", "Görev", "Konu"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.load_pomodoros()

        # Silme Butonu
        self.delete_button = QPushButton("Seçili Pomodoroları Sil")
        self.delete_button.clicked.connect(self.delete_pomodoros)

        layout.addLayout(date_range_layout)
        layout.addLayout(topic_layout)
        layout.addWidget(self.table)
        layout.addWidget(self.delete_button)

        self.setLayout(layout)

    def set_default_week_dates(self):
        today = self.get_local_time().date()
        start_date = today - datetime.timedelta(days=today.weekday())  # Haftanın başlangıcı
        end_date = start_date + datetime.timedelta(days=6)  # Haftanın sonu
        self.start_date_edit.setDate(start_date)
        self.end_date_edit.setDate(end_date)

    def load_topics(self):
        self.topic_combobox.clear()
        self.topic_combobox.addItem("Tüm Konular")
        topics = self.session.query(Topic).all()
        for topic in topics:
            self.topic_combobox.addItem(topic.name)

    def load_pomodoros(self):
        start_date = self.start_date_edit.date().toPyDate()
        end_date = self.end_date_edit.date().toPyDate()
        topic_name = self.topic_combobox.currentText()

        query = self.session.query(Pomodoro).filter(Pomodoro.date >= start_date, Pomodoro.date <= end_date)
        if topic_name != "Tüm Konular":
            topic = self.session.query(Topic).filter_by(name=topic_name).first()
            if topic:
                query = query.filter_by(topic_id=topic.id)

        pomodoros = query.all()

        self.table.setRowCount(len(pomodoros))
        for row, pomodoro in enumerate(pomodoros):
            topic = self.session.query(Topic).filter_by(id=pomodoro.topic_id).first()
            topic_name = topic.name if topic else "Bilinmeyen"
            self.table.setItem(row, 0, QTableWidgetItem(str(pomodoro.id)))
            self.table.setItem(row, 1, QTableWidgetItem(pomodoro.date.strftime('%Y-%m-%d')))
            self.table.setItem(row, 2, QTableWidgetItem(str(pomodoro.duration)))
            self.table.setItem(row, 3, QTableWidgetItem(pomodoro.task))
            self.table.setItem(row, 4, QTableWidgetItem(topic_name))

    def delete_pomodoros(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek istediğiniz pomodoroları seçin.")
            return

        reply = QMessageBox.warning(self, "Dikkat",
                                    "Seçili pomodoroları silmek üzeresiniz. Bu işlem geri alınamaz!\nDevam etmek istediğinizden emin misiniz?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                for row in selected_rows:
                    pomodoro_id = int(self.table.item(row.row(), 0).text())
                    pomodoro = self.session.query(Pomodoro).filter_by(id=pomodoro_id).first()
                    if pomodoro:
                        self.session.delete(pomodoro)
                self.session.commit()
                self.load_pomodoros()
                self.pomodoro_deleted.emit()
                QMessageBox.information(self, "Başarılı", "Seçili pomodorolar başarıyla silindi.")
            except Exception as e:
                self.session.rollback()
                QMessageBox.critical(self, "Hata", f"Pomodorolar silinirken bir hata oluştu: {e}")

