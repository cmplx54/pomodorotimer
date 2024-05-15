# report.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton, QMessageBox, QFrame, QDateEdit, \
    QPushButton, QComboBox
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from models import get_session, get_engine, Pomodoro, Topic
import datetime
import matplotlib.dates as mdates


class ReportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Rapor Formu")
        self.setGeometry(200, 200, 800, 800)  # Formun boyutu artırıldı
        self.engine = get_engine()
        self.session = get_session(self.engine)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Radio Buttons
        self.weekly_radio = QRadioButton("Haftalık")
        self.monthly_radio = QRadioButton("Aylık")
        self.yearly_radio = QRadioButton("Yıllık")
        self.custom_radio = QRadioButton("Özel Tarih Aralığı")
        self.weekly_radio.setChecked(True)  # Varsayılan olarak haftalık seçili

        self.weekly_radio.toggled.connect(self.show_report)
        self.monthly_radio.toggled.connect(self.show_report)
        self.yearly_radio.toggled.connect(self.show_report)
        self.custom_radio.toggled.connect(self.show_custom_report)

        radio_layout = QHBoxLayout()
        radio_layout.addWidget(self.weekly_radio)
        radio_layout.addWidget(self.monthly_radio)
        radio_layout.addWidget(self.yearly_radio)
        radio_layout.addWidget(self.custom_radio)

        # Tarih Aralığı Seçimi
        self.start_date_edit = QDateEdit(calendarPopup=True)
        self.start_date_edit.setDate(QDate.currentDate().addMonths(-1))  # Varsayılan olarak bir ay önce
        self.end_date_edit = QDateEdit(calendarPopup=True)
        self.end_date_edit.setDate(QDate.currentDate())  # Varsayılan olarak bugün
        self.date_range_button = QPushButton("Raporu Göster")
        self.date_range_button.clicked.connect(self.show_custom_report)

        date_range_layout = QHBoxLayout()
        date_range_layout.addWidget(QLabel("Başlangıç Tarihi:"))
        date_range_layout.addWidget(self.start_date_edit)
        date_range_layout.addWidget(QLabel("Bitiş Tarihi:"))
        date_range_layout.addWidget(self.end_date_edit)
        date_range_layout.addWidget(self.date_range_button)

        # Konu Seçimi
        self.topic_combobox = QComboBox()
        self.load_topics()
        self.topic_combobox.currentTextChanged.connect(self.show_report)  # Konu değiştiğinde raporu güncelle

        topic_layout = QHBoxLayout()
        topic_layout.addWidget(QLabel("Konu:"))
        topic_layout.addWidget(self.topic_combobox)

        # Sonuç Etiketleri
        label_font = QFont('Arial', 14, QFont.Bold)
        value_font = QFont('Arial', 18, QFont.Bold)

        self.total_pomodoro_label = QLabel("Toplam Pomodoro Sayısı:")
        self.total_pomodoro_label.setFont(label_font)

        self.total_pomodoro_value = QLabel("0")
        self.total_pomodoro_value.setFont(value_font)
        self.total_pomodoro_value.setStyleSheet("color: blue;")

        self.total_duration_label = QLabel("Toplam Süre:")
        self.total_duration_label.setFont(label_font)

        self.total_duration_value = QLabel("0 saat")
        self.total_duration_value.setFont(value_font)
        self.total_duration_value.setStyleSheet("color: blue;")

        total_pomodoro_layout = QHBoxLayout()
        total_pomodoro_layout.addWidget(self.total_pomodoro_label)
        total_pomodoro_layout.addWidget(self.total_pomodoro_value)

        total_duration_layout = QHBoxLayout()
        total_duration_layout.addWidget(self.total_duration_label)
        total_duration_layout.addWidget(self.total_duration_value)

        result_layout = QVBoxLayout()
        result_layout.addLayout(total_pomodoro_layout)
        result_layout.addLayout(total_duration_layout)
        result_layout.setContentsMargins(0, 0, 0, 0)  # Üst ve alt kenar marjinlerini azaltma

        # Grafik için Matplotlib Figure ve Canvas
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        layout.addLayout(radio_layout)
        layout.addLayout(date_range_layout)
        layout.addLayout(topic_layout)
        layout.addLayout(result_layout)
        layout.addWidget(self.canvas)

        self.setLayout(layout)
        self.show_report()  # Başlangıçta haftalık raporu göster

    def load_topics(self):
        self.topic_combobox.clear()
        self.topic_combobox.addItem("Tüm Konular")
        topics = self.session.query(Topic).all()
        for topic in topics:
            self.topic_combobox.addItem(topic.name)

    def show_report(self):
        today = datetime.datetime.now().date()

        if self.weekly_radio.isChecked():
            start_date = today - datetime.timedelta(days=today.weekday())  # Haftanın başlangıcı
            end_date = start_date + datetime.timedelta(days=7)
            self.plot_report(start_date, end_date)
        elif self.monthly_radio.isChecked():
            start_date = today.replace(day=1)  # Ayın başlangıcı
            end_date = (today.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)  # Ayın sonu
            self.plot_report(start_date, end_date)
        elif self.yearly_radio.isChecked():
            start_date = today.replace(month=1, day=1)  # Yılın başlangıcı
            end_date = today.replace(month=12, day=31)  # Yılın sonu
            self.plot_report(start_date, end_date)

    def show_custom_report(self):
        if self.custom_radio.isChecked() or self.sender() == self.date_range_button:
            start_date = self.start_date_edit.date().toPyDate()
            end_date = self.end_date_edit.date().toPyDate()
            self.plot_report(start_date, end_date)

    def plot_report(self, start_date, end_date):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        dates = []
        durations = []

        total_pomodoro_count = 0
        total_duration = 0

        topic_name = self.topic_combobox.currentText()
        topic = self.session.query(Topic).filter_by(name=topic_name).first() if topic_name != "Tüm Konular" else None

        delta = (end_date - start_date).days + 1  # +1 dahil edilmesi için

        for i in range(delta):
            single_date = start_date + datetime.timedelta(days=i)
            query = self.session.query(Pomodoro).filter(Pomodoro.date >= single_date,
                                                        Pomodoro.date < single_date + datetime.timedelta(days=1))
            if topic:
                query = query.filter_by(topic_id=topic.id)
            daily_durations = query.with_entities(Pomodoro.duration).all()
            daily_duration = sum(duration[0] for duration in daily_durations)
            dates.append(single_date)
            durations.append(daily_duration)

            total_pomodoro_count += query.count()
            total_duration += daily_duration

        ax.plot(dates, durations)
        title = f'Pomodoro Süreleri ({start_date} - {end_date})'
        if topic:
            title += f' - Konu: {topic.name}'
        ax.set_title(title)
        ax.set_xlabel('Tarih')
        ax.set_ylabel('Toplam Süre (dakika)')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        for label in ax.get_xticklabels():
            label.set_rotation(90)  # x eksenindeki yazıları dikey yapar

        self.figure.tight_layout()
        self.figure.subplots_adjust(bottom=0.25)  # x ekseni etiketleri için daha fazla boşluk bırak
        self.canvas.draw()

        self.total_pomodoro_value.setText(str(total_pomodoro_count))
        self.total_duration_value.setText(f"{total_duration // 60} saat {total_duration % 60} dakika")
