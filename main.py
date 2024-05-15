import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QDialog
from PyQt5.QtMultimedia import QSound
from gui import PomodoroTimerGUI
from settings import SettingsDialog
from history import HistoryDialog
from report import ReportDialog
from total_time_by_topic import TotalTimeByTopicDialog
from about import AboutDialog
from models import get_engine, get_session, Pomodoro, Topic
import datetime
import pytz

class PomodoroTimerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.time_left = 0  # Geri sayım süresi (saniye cinsinden)
        self.is_running = False  # Timer'ın çalışıp çalışmadığını kontrol eder
        self.is_delay = False  # Şu anda delay time geri sayımı olup olmadığını kontrol eder

        self.engine = get_engine() # veritabanı
        self.session = get_session(self.engine) # veritabanı

        self.gui = PomodoroTimerGUI(
            self.start_timer, self.pause_timer, self.resume_timer, self.reset_timer, self.skip_delay
        )

        self.initUI()
        self.timer = self.gui.timer
        self.timer.timeout.connect(self.update_timer)
        self.load_topics()
        self.load_today_pomodoros()

    def get_local_time(self):
        local_tz = pytz.timezone('Europe/Istanbul')  # Yerel zaman diliminizi burada ayarlayın
        return datetime.datetime.now(local_tz)

    def initUI(self):
        self.setCentralWidget(self.gui)
        menubar = self.menuBar()

        settings_action = QAction("Ayarlar", self)
        settings_action.triggered.connect(self.open_settings)
        menubar.addAction(settings_action)

        history_action = QAction("Geçmiş Pomodorolar", self)
        history_action.triggered.connect(self.open_history)
        menubar.addAction(history_action)

        report_action = QAction("Rapor", self)
        report_action.triggered.connect(self.open_report)
        menubar.addAction(report_action)

        total_time_action = QAction("Toplam Zaman", self)
        total_time_action.triggered.connect(self.open_total_time)
        menubar.addAction(total_time_action)

        about_action = QAction("Hakkında", self)
        about_action.triggered.connect(self.open_about)
        menubar.addAction(about_action)

        self.setWindowTitle("Pomodoro Zamanlayıcı")
        self.setGeometry(100, 100, 1000, 600)  # Form genişletildi

    def open_settings(self):
        try:
            dialog = SettingsDialog(self)
            dialog.topic_added.connect(self.load_topics)  # Sinyal bağlandı
            dialog.exec_()
        except Exception as e:
            print(f"Ayarları açarken hata oluştu: {e}")

    def open_history(self):
        try:
            dialog = HistoryDialog(self)
            dialog.pomodoro_deleted.connect(self.load_today_pomodoros)  # Sinyal bağlandı
            dialog.exec_()
        except Exception as e:
            print(f"Geçmiş pomodoroları açarken hata oluştu: {e}")

    def open_report(self):
        try:
            dialog = ReportDialog(self)
            dialog.exec_()
        except Exception as e:
            print(f"Raporu açarken hata oluştu: {e}")

    def open_total_time(self):
        try:
            dialog = TotalTimeByTopicDialog(self)
            dialog.exec_()
        except Exception as e:
            print(f"Toplam Zamanı açarken hata oluştu: {e}")

    def open_about(self):
        try:
            dialog = AboutDialog(self)
            dialog.exec_()
        except Exception as e:
            print(f"Hakkında sayfasını açarken hata oluştu: {e}")

    def start_timer(self):
        self.time_left = self.gui.work_time.value() * 60  # Çalışma süresini saniyeye çevir
        self.gui.update_timer_label(self.time_left)
        self.timer.start(1000)  # Timer'ı 1 saniyelik aralıklarla çalıştır
        self.gui.start_button.setEnabled(False)
        self.gui.pause_button.setEnabled(True)
        self.gui.resume_button.setEnabled(False)
        self.is_running = True

    def pause_timer(self):
        if self.timer.isActive():
            self.timer.stop()
            self.gui.pause_button.setEnabled(False)
            self.gui.resume_button.setEnabled(True)

    def resume_timer(self):
        if not self.timer.isActive() and self.is_running:
            self.timer.start(1000)
            self.gui.pause_button.setEnabled(True)
            self.gui.resume_button.setEnabled(False)

    def update_timer(self):
        try:
            if self.time_left > 0:
                self.time_left -= 1
                self.gui.update_timer_label(self.time_left)
            else:
                self.timer.stop()
                if self.is_delay:
                    self.is_delay = False
                    self.start_timer()
                    self.gui.skip_button.setVisible(False)
                else:
                    self.is_running = False
                    self.gui.start_button.setEnabled(True)
                    self.gui.pause_button.setEnabled(False)
                    self.gui.resume_button.setEnabled(False)
                    self.save_pomodoro(self.gui.work_time.value())
                    self.play_sound()
                    self.start_delay_timer()
        except Exception as e:
            print(f"Zamanlayıcı güncellenirken hata oluştu: {e}")

    def start_delay_timer(self):
        self.is_delay = True
        self.time_left = self.gui.break_time.value() * 60
        self.gui.update_timer_label(self.time_left)
        self.timer.start(1000)
        self.gui.skip_button.setVisible(True)
        self.gui.pause_button.setEnabled(True)
        self.gui.resume_button.setEnabled(False)

    def skip_delay(self):
        self.timer.stop()
        self.is_delay = False
        self.start_timer()
        self.gui.skip_button.setVisible(False)

    def reset_timer(self):
        self.timer.stop()
        self.is_running = False
        self.is_delay = False
        self.time_left = self.gui.work_time.value() * 60  # Çalışma süresini saniyeye çevir
        self.gui.update_timer_label(self.time_left)
        self.gui.start_button.setEnabled(True)
        self.gui.pause_button.setEnabled(False)
        self.gui.resume_button.setEnabled(False)
        self.gui.skip_button.setVisible(False)

    def play_sound(self):
        try:
            QSound.play("alarm.wav")  # alarm.wav dosyasını oynat
        except Exception as e:
            print(f"Ses çalınırken hata oluştu: {e}")

    def save_pomodoro(self, duration):
        try:
            task = self.gui.text_box.text()
            topic_name = self.gui.select_box.currentText()
            topic = self.session.query(Topic).filter_by(name=topic_name).first()
            if not topic:
                topic = Topic(name=topic_name)
                self.session.add(topic)
                self.session.commit()
            pomodoro = Pomodoro(duration=duration, task=task, topic_id=topic.id, date=self.get_local_time())
            self.session.add(pomodoro)
            self.session.commit()
            self.update_pomodoro_list(pomodoro.id)
            self.update_today_count()
            self.update_total_work_time()
        except Exception as e:
            print(f"Pomodoro kaydedilirken hata oluştu: {e}")

    def load_topics(self):
        try:
            topics = self.session.query(Topic).all()
            self.gui.select_box.clear()
            if topics:
                for topic in topics:
                    self.gui.select_box.addItem(topic.name)
                self.gui.select_box.setCurrentIndex(0)
            else:
                self.gui.select_box.addItem("Seçenek Seç")
        except Exception as e:
            print(f"Konular yüklenirken hata oluştu: {e}")

    def load_today_pomodoros(self):
        try:
            today = self.get_local_time().date()
            pomodoros = self.session.query(Pomodoro).filter(Pomodoro.date >= today).all()
            self.gui.clear_pomodoro_list()
            total_minutes = 0
            for pomodoro in pomodoros:
                topic = self.session.query(Topic).filter_by(id=pomodoro.topic_id).first()
                topic_name = topic.name if topic else "Bilinmeyen"
                self.gui.add_pomodoro_to_list(pomodoro.id, pomodoro.date, pomodoro.duration, pomodoro.task, topic_name)
                total_minutes += pomodoro.duration
            self.update_today_count()
            self.gui.update_total_work_time(total_minutes)
        except Exception as e:
            print(f"Bugünkü pomodorolar yüklenirken hata oluştu: {e}")

    def update_today_count(self):
        try:
            today = self.get_local_time().date()
            count = self.session.query(Pomodoro).filter(Pomodoro.date >= today).count()
            self.gui.pomodoro_count_value.setText(str(count))
        except Exception as e:
            print(f"Bugünkü pomodoro sayısı güncellenirken hata oluştu: {e}")

    def update_total_work_time(self):
        try:
            today = self.get_local_time().date()
            total_minutes = self.session.query(Pomodoro).filter(Pomodoro.date >= today).with_entities(Pomodoro.duration).all()
            total_minutes = sum(duration[0] for duration in total_minutes)
            self.gui.update_total_work_time(total_minutes)
        except Exception as e:
            print(f"Toplam çalışma süresi güncellenirken hata oluştu: {e}")

    def update_pomodoro_list(self, pomodoro_id):
        try:
            pomodoro = self.session.query(Pomodoro).filter_by(id=pomodoro_id).first()
            if pomodoro:
                topic = self.session.query(Topic).filter_by(id=pomodoro.topic_id).first()
                topic_name = topic.name if topic else "Bilinmeyen"
                self.gui.add_pomodoro_to_list(pomodoro.id, pomodoro.date, pomodoro.duration, pomodoro.task, topic_name)
        except Exception as e:
            print(f"Pomodoro listesi güncellenirken hata oluştu: {e}")

    def run(self):
        self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pomodoro_app = PomodoroTimerApp()
    pomodoro_app.run()
    sys.exit(app.exec_())
