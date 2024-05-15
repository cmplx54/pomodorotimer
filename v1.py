import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, \
    QListWidget, QSpinBox, QSizePolicy, QSpacerItem
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtMultimedia import QSound
import datetime


class PomodoroTimer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pomodoro Timer")
        self.setGeometry(100, 100, 600, 400)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.time_left = 0  # Geri sayım süresi (saniye cinsinden)
        self.is_running = False  # Timer'ın çalışıp çalışmadığını kontrol eder
        self.is_delay = False  # Şu anda delay time geri sayımı olup olmadığını kontrol eder

        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout()

        # Font ayarları
        label_font = QFont('Arial', 14, QFont.Bold)
        value_font = QFont('Arial', 20)
        timer_font = QFont('Arial', 40, QFont.Bold)

        # Sol panel
        left_panel = QVBoxLayout()
        left_panel.setAlignment(Qt.AlignTop)

        # Pomodoro Count
        pomodoro_count_layout = QVBoxLayout()
        self.pomodoro_count_label = QLabel("Today Count")
        self.pomodoro_count_label.setFont(label_font)
        self.pomodoro_count_label.setAlignment(Qt.AlignCenter)
        self.pomodoro_count_label.setStyleSheet("color: black;")

        self.pomodoro_count_value = QLabel("0")
        self.pomodoro_count_value.setFont(value_font)
        self.pomodoro_count_value.setAlignment(Qt.AlignCenter)
        self.pomodoro_count_value.setStyleSheet("color: blue;")

        pomodoro_count_layout.addWidget(self.pomodoro_count_label)
        pomodoro_count_layout.addWidget(self.pomodoro_count_value)

        # Working Time
        work_time_layout = QVBoxLayout()
        self.work_label = QLabel("Working Time")
        self.work_label.setFont(label_font)
        self.work_label.setAlignment(Qt.AlignCenter)
        self.work_label.setStyleSheet("color: black;")

        self.work_time = QSpinBox()
        self.work_time.setFont(value_font)
        self.work_time.setValue(25)
        self.work_time.setRange(1, 60)
        self.work_time.setAlignment(Qt.AlignCenter)
        self.work_time.setStyleSheet("color: blue;")

        work_time_layout.addWidget(self.work_label)
        work_time_layout.addWidget(self.work_time)

        # Delay Time
        break_time_layout = QVBoxLayout()
        self.break_label = QLabel("Delay Time")
        self.break_label.setFont(label_font)
        self.break_label.setAlignment(Qt.AlignCenter)
        self.break_label.setStyleSheet("color: black;")

        self.break_time = QSpinBox()
        self.break_time.setFont(value_font)
        self.break_time.setValue(5)
        self.break_time.setRange(1, 60)
        self.break_time.setAlignment(Qt.AlignCenter)
        self.break_time.setStyleSheet("color: blue;")

        break_time_layout.addWidget(self.break_label)
        break_time_layout.addWidget(self.break_time)

        self.start_button = QPushButton("Start")
        self.start_button.setFont(label_font)
        self.start_button.setStyleSheet("margin-top: 10px;")
        self.start_button.clicked.connect(self.start_timer)

        self.pause_button = QPushButton("Dur")
        self.pause_button.setFont(label_font)
        self.pause_button.setStyleSheet("margin-top: 10px;")
        self.pause_button.clicked.connect(self.pause_timer)
        self.pause_button.setEnabled(False)

        self.resume_button = QPushButton("Devam Et")
        self.resume_button.setFont(label_font)
        self.resume_button.setStyleSheet("margin-top: 10px;")
        self.resume_button.clicked.connect(self.resume_timer)
        self.resume_button.setEnabled(False)

        self.reset_button = QPushButton("Reset")
        self.reset_button.setFont(label_font)
        self.reset_button.setStyleSheet("margin-top: 10px;")
        self.reset_button.clicked.connect(self.reset_timer)

        self.skip_button = QPushButton("X")
        self.skip_button.setFont(label_font)
        self.skip_button.setFixedSize(30, 30)
        self.skip_button.setStyleSheet("margin-top: 10px;")
        self.skip_button.clicked.connect(self.skip_delay)
        self.skip_button.setVisible(False)

        # Timer label
        self.timer_label = QLabel("25:00")
        self.timer_label.setFont(timer_font)
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("color: blue;")

        left_panel.addLayout(pomodoro_count_layout)
        left_panel.addLayout(work_time_layout)
        left_panel.addLayout(break_time_layout)
        left_panel.addWidget(self.start_button)
        left_panel.addWidget(self.pause_button)
        left_panel.addWidget(self.resume_button)
        left_panel.addWidget(self.reset_button)
        left_panel.addWidget(self.timer_label)
        left_panel.addWidget(self.skip_button, alignment=Qt.AlignRight)

        # Sol paneli sağa kaydırmak için spacer
        left_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        # Sağ panel
        right_panel = QVBoxLayout()

        self.today_pomodoro_list_label = QLabel("Today's Pomodoro List")
        self.today_pomodoro_list_label.setFont(label_font)
        self.today_pomodoro_list_label.setAlignment(Qt.AlignCenter)
        self.today_pomodoro_list = QListWidget()

        right_panel.addWidget(self.today_pomodoro_list_label)
        right_panel.addWidget(self.today_pomodoro_list)

        right_panel.setStretch(1, 1)

        # Ana layout
        main_layout.addLayout(left_panel)
        main_layout.addSpacing(40)  # Sol ve sağ panel arasına boşluk eklemek için
        main_layout.addLayout(right_panel, 1)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def start_timer(self):
        self.time_left = self.work_time.value() * 60  # Çalışma süresini saniyeye çevir
        self.update_timer_label()
        self.timer.start(1000)  # Timer'ı 1 saniyelik aralıklarla çalıştır
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.resume_button.setEnabled(False)
        self.is_running = True

    def pause_timer(self):
        if self.timer.isActive():
            self.timer.stop()
            self.pause_button.setEnabled(False)
            self.resume_button.setEnabled(True)

    def resume_timer(self):
        if not self.timer.isActive() and self.is_running:
            self.timer.start(1000)
            self.pause_button.setEnabled(True)
            self.resume_button.setEnabled(False)

    def update_timer(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.update_timer_label()
        else:
            self.timer.stop()
            if self.is_delay:
                self.is_delay = False
                self.start_timer()
                self.skip_button.setVisible(False)
            else:
                self.is_running = False
                self.start_button.setEnabled(True)
                self.pause_button.setEnabled(False)
                self.resume_button.setEnabled(False)
                self.add_pomodoro_to_list()
                self.play_sound()
                self.start_delay_timer()

    def update_timer_label(self):
        minutes, seconds = divmod(self.time_left, 60)
        self.timer_label.setText(f"{minutes:02d}:{seconds:02d}")

    def add_pomodoro_to_list(self):
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.today_pomodoro_list.addItem(f"{current_time} - {self.work_time.value()} min")
        pomodoro_count = int(self.pomodoro_count_value.text()) + 1
        self.pomodoro_count_value.setText(str(pomodoro_count))

    def start_delay_timer(self):
        self.is_delay = True
        self.time_left = self.break_time.value() * 60
        self.update_timer_label()
        self.timer.start(1000)
        self.skip_button.setVisible(True)
        self.pause_button.setEnabled(True)
        self.resume_button.setEnabled(False)

    def skip_delay(self):
        self.timer.stop()
        self.is_delay = False
        self.start_timer()
        self.skip_button.setVisible(False)

    def reset_timer(self):
        self.timer.stop()
        self.is_running = False
        self.is_delay = False
        self.time_left = self.work_time.value() * 60  # Çalışma süresini saniyeye çevir
        self.update_timer_label()
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.resume_button.setEnabled(False)
        self.skip_button.setVisible(False)

    def play_sound(self):
        QSound.play("alarm.wav")  # alarm.wav dosyasını oynat


app = QApplication([])
window = PomodoroTimer()
window.show()
app.exec_()
