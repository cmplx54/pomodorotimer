# gui.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, \
    QSpinBox, QComboBox, QLineEdit
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont
import datetime


class PomodoroTimerGUI(QWidget):
    def __init__(self, start_callback, pause_callback, resume_callback, reset_callback, skip_callback):
        super().__init__()

        self.timer = QTimer()

        self.start_callback = start_callback
        self.pause_callback = pause_callback
        self.resume_callback = resume_callback
        self.reset_callback = reset_callback
        self.skip_callback = skip_callback

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

        # Dikey metin
        vertical_text = QLabel("G\nk\nş\nn\n \nP\nr\nj\n.")
        vertical_font = QFont('Arial', 12, QFont.Bold)
        vertical_text.setFont(vertical_font)
        vertical_text.setStyleSheet("color: black;")
        vertical_text.setAlignment(Qt.AlignCenter)
        vertical_text.setFixedWidth(30)

        # Pomodoro Count
        pomodoro_count_layout = QHBoxLayout()
        self.pomodoro_count_label = QLabel("Bugünkü sayı")
        self.pomodoro_count_label.setFont(label_font)
        self.pomodoro_count_label.setStyleSheet("color: black;")

        self.pomodoro_count_value = QLabel("0")
        self.pomodoro_count_value.setFont(value_font)
        self.pomodoro_count_value.setStyleSheet("color: blue;")

        pomodoro_count_layout.addWidget(self.pomodoro_count_label)
        pomodoro_count_layout.addWidget(self.pomodoro_count_value)

        # Working Time
        work_time_layout = QHBoxLayout()
        self.work_label = QLabel("Pomodora Süresi")
        self.work_label.setFont(label_font)
        self.work_label.setStyleSheet("color: black;")

        self.work_time = QSpinBox()
        self.work_time.setFont(value_font)
        self.work_time.setValue(25)
        self.work_time.setRange(1, 60)
        self.work_time.setStyleSheet("color: blue;")

        work_time_layout.addWidget(self.work_label)
        work_time_layout.addWidget(self.work_time)

        # Delay Time
        break_time_layout = QHBoxLayout()
        self.break_label = QLabel("Dinlenme süresi")
        self.break_label.setFont(label_font)
        self.break_label.setStyleSheet("color: black;")

        self.break_time = QSpinBox()
        self.break_time.setFont(value_font)
        self.break_time.setValue(5)
        self.break_time.setRange(1, 60)
        self.break_time.setStyleSheet("color: blue;")

        break_time_layout.addWidget(self.break_label)
        break_time_layout.addWidget(self.break_time)

        # Select Box ve Text Box
        select_text_layout = QHBoxLayout()
        self.select_box = QComboBox()
        self.select_box.setFont(value_font)
        self.select_box.setEditable(True)
        self.select_box.addItem("Select Option")  # Gelecekte kullanılacak
        self.text_box = QLineEdit()
        self.text_box.setFont(value_font)
        self.text_box.setPlaceholderText("Task gir")

        select_text_layout.addWidget(self.select_box)
        select_text_layout.addWidget(self.text_box)

        self.start_button = QPushButton("Start")
        self.start_button.setFont(label_font)
        self.start_button.setStyleSheet("margin-top: 10px;")
        self.start_button.clicked.connect(self.start_callback)

        self.pause_button = QPushButton("Dur")
        self.pause_button.setFont(label_font)
        self.pause_button.setStyleSheet("margin-top: 10px;")
        self.pause_button.clicked.connect(self.pause_callback)
        self.pause_button.setEnabled(False)

        self.resume_button = QPushButton("Devam Et")
        self.resume_button.setFont(label_font)
        self.resume_button.setStyleSheet("margin-top: 10px;")
        self.resume_button.clicked.connect(self.resume_callback)
        self.resume_button.setEnabled(False)

        self.reset_button = QPushButton("Reset")
        self.reset_button.setFont(label_font)
        self.reset_button.setStyleSheet("margin-top: 10px;")
        self.reset_button.clicked.connect(self.reset_callback)

        self.skip_button = QPushButton("X")
        self.skip_button.setFont(label_font)
        self.skip_button.setFixedSize(30, 30)
        self.skip_button.setStyleSheet("margin-top: 10px;")
        self.skip_button.clicked.connect(self.skip_callback)
        self.skip_button.setVisible(False)

        # Timer label
        self.timer_label = QLabel("25:00")
        self.timer_label.setFont(timer_font)
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("color: blue;")

        # Yeni yatay layout, dikey metin ve sayacı yan yana yerleştirir
        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(vertical_text)
        horizontal_layout.addWidget(self.timer_label)

        left_panel.addLayout(horizontal_layout)
        left_panel.addLayout(pomodoro_count_layout)
        left_panel.addLayout(work_time_layout)
        left_panel.addLayout(break_time_layout)
        left_panel.addLayout(select_text_layout)
        left_panel.addWidget(self.start_button)
        left_panel.addWidget(self.pause_button)
        left_panel.addWidget(self.resume_button)
        left_panel.addWidget(self.reset_button)
        left_panel.addWidget(self.skip_button, alignment=Qt.AlignRight)

        # Sağ panel
        right_panel = QVBoxLayout()

        self.today_pomodoro_list_label = QLabel("Today's Pomodoro List")
        self.today_pomodoro_list_label.setFont(label_font)
        self.today_pomodoro_list_label.setAlignment(Qt.AlignCenter)
        self.today_pomodoro_list = QTableWidget()
        self.today_pomodoro_list.setColumnCount(5)
        self.today_pomodoro_list.setHorizontalHeaderLabels(["ID", "Time", "Duration", "Task", "Topic"])
        self.today_pomodoro_list.setFixedWidth(600)  # Liste genişliği artırıldı

        # Toplam çalışma süresi
        self.total_work_label = QLabel("Total Work Time:")
        self.total_work_label.setFont(label_font)
        self.total_work_label.setStyleSheet("color: black;")
        self.total_work_value = QLabel("0 hours")
        self.total_work_value.setFont(value_font)
        self.total_work_value.setStyleSheet("color: blue;")

        total_work_layout = QHBoxLayout()
        total_work_layout.addWidget(self.total_work_label)
        total_work_layout.addWidget(self.total_work_value)

        right_panel.addWidget(self.today_pomodoro_list_label)
        right_panel.addWidget(self.today_pomodoro_list)
        right_panel.addLayout(total_work_layout)

        right_panel.setStretch(1, 1)

        # Ana layout
        main_layout.addLayout(left_panel)
        main_layout.addSpacing(20)  # Sol ve sağ panel arasına boşluk eklemek için
        main_layout.addLayout(right_panel, 1)

        self.setLayout(main_layout)

    def update_timer_label(self, time_left):
        minutes, seconds = divmod(time_left, 60)
        self.timer_label.setText(f"{minutes:02d}:{seconds:02d}")

    def add_pomodoro_to_list(self, pomodoro_id, time, duration, task, topic):
        row_position = self.today_pomodoro_list.rowCount()
        self.today_pomodoro_list.insertRow(row_position)
        self.today_pomodoro_list.setItem(row_position, 0, QTableWidgetItem(str(pomodoro_id)))
        self.today_pomodoro_list.setItem(row_position, 1, QTableWidgetItem(time.strftime("%H:%M:%S")))
        self.today_pomodoro_list.setItem(row_position, 2, QTableWidgetItem(str(duration)))
        self.today_pomodoro_list.setItem(row_position, 3, QTableWidgetItem(task))
        self.today_pomodoro_list.setItem(row_position, 4, QTableWidgetItem(topic))

    def clear_pomodoro_list(self):
        self.today_pomodoro_list.setRowCount(0)

    def update_total_work_time(self, total_minutes):
        hours, minutes = divmod(total_minutes, 60)
        self.total_work_value.setText(f"{hours} hours {minutes} minutes")
