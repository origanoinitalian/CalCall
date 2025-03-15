import enum
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Enum as SQLAlchemyEnum
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


class AppointmentStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class User(Base):
    __tablename__ = 'users'
    telegram_id = Column(Integer, primary_key=True)
    target_calendar_id = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)  #who can access the bot in what level  
    

class Appointment(Base):
    __tablename__ = 'appointments'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer)
    target_calendar_id = Column(String, nullable=False)
    date_time = Column(DateTime)
    status = Column(SQLAlchemyEnum(AppointmentStatus), default=AppointmentStatus.PENDING)
    # maybe other relevant appointment details later on

Base.metadata.create_all(engine)

def get_user(telegram_id):
    session = Session()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    session.close()
    return user

def create_or_update_user(telegram_id, target_calendar_id):
    session = Session()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if user:
        user.target_calendar_id = target_calendar_id
    else:
        user = User(telegram_id=telegram_id, target_calendar_id=target_calendar_id)
        session.add(user)
    session.commit()
    session.close()

def create_appointment(telegram_id, target_calendar_id, date_time):
    session = Session()
    appointment = Appointment(telegram_id=telegram_id, target_calendar_id=target_calendar_id, date_time=date_time)
    session.add(appointment)
    session.commit()
    session.close()

