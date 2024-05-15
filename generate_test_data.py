# generate_test_data.py
import random
import datetime
from models import get_engine, get_session, Pomodoro, Topic

# Veritabanı bağlantısını oluştur
engine = get_engine()
session = get_session(engine)

# Konu (Topic) oluştur ve ekle
topics = ["Work", "Study", "Exercise", "Reading", "Coding", "Project"]
for topic_name in topics:
    if not session.query(Topic).filter_by(name=topic_name).first():
        topic = Topic(name=topic_name)
        session.add(topic)


# Rastgele bir tarih oluştur
def random_date(start, end):
    return start + datetime.timedelta(
        seconds=random.randint(0, int((end - start).total_seconds())),
    )


# Rastgele veriler oluştur ve ekle
start_date = datetime.datetime.now() - datetime.timedelta(days=3 * 365)
end_date = datetime.datetime.now()

for _ in range(2000):  # 1000 adet rastgele veri ekle
    topic_id = random.choice(session.query(Topic).all()).id
    duration = random.randint(15, 60)  # Pomodoro süresi 15-60 dakika arasında
    date = random_date(start_date, end_date)
    task = random.choice(["Task A", "Task B", "Task C", "Task D"])

    pomodoro = Pomodoro(date=date, duration=duration, task=task, topic_id=topic_id)
    session.add(pomodoro)

# Veritabanına işlemleri kaydet
session.commit()

print("Test verileri başarıyla eklendi.")
