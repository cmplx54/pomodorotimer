# models.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime

Base = declarative_base()

class Topic(Base):
    __tablename__ = 'topics'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)

class Pomodoro(Base):
    __tablename__ = 'pomodoros'
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    duration = Column(Integer, nullable=False)
    task = Column(String, nullable=False)
    topic_id = Column(Integer, ForeignKey('topics.id'))

    topic = relationship('Topic')

def get_engine():
    return create_engine('sqlite:///pomodoro.db')

def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()

if __name__ == '__main__':
    engine = get_engine()
    Base.metadata.create_all(engine)
