# total_time_by_topic.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QDateEdit, QPushButton, QTableWidget, \
    QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from models import get_session, get_engine, Pomodoro, Topic
import datetime
import pytz


class TotalTimeByTopicDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tüm Konuların Toplam Süresi")
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
        self.start_date_edit.setDate(QDate.currentDate().addMonths(-1))  # Varsayılan olarak bir ay önce
        self.end_date_edit = QDateEdit(calendarPopup=True)
        self.end_date_edit.setDate(QDate.currentDate())  # Varsayılan olarak bugün
        self.date_range_button = QPushButton("Toplam Süreyi Göster")
        self.date_range_button.clicked.connect(self.show_total_time)

        date_range_layout = QHBoxLayout()
        date_range_layout.addWidget(QLabel("Başlangıç Tarihi:"))
        date_range_layout.addWidget(self.start_date_edit)
        date_range_layout.addWidget(QLabel("Bitiş Tarihi:"))
        date_range_layout.addWidget(self.end_date_edit)
        date_range_layout.addWidget(self.date_range_button)

        # Toplam Süre Tablosu
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Konu", "Toplam Süre (dakika)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addLayout(date_range_layout)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def show_total_time(self):
        start_date = self.start_date_edit.date().toPyDate()
        end_date = self.end_date_edit.date().toPyDate()

        topics = self.session.query(Topic).all()
        self.table.setRowCount(len(topics))

        for row, topic in enumerate(topics):
            total_duration = self.session.query(Pomodoro).filter(Pomodoro.topic_id == topic.id,
                                                                 Pomodoro.date >= start_date,
                                                                 Pomodoro.date <= end_date).with_entities(
                Pomodoro.duration).all()
            total_duration = sum(duration[0] for duration in total_duration)
            self.table.setItem(row, 0, QTableWidgetItem(topic.name))
            self.table.setItem(row, 1, QTableWidgetItem(str(total_duration)))

