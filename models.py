from enum import unique
from operator import index
from pymysql import Timestamp
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, func, DateTime, Enum, Time
from sqlalchemy.orm import relationship
from db import Base
from sqlalchemy.orm import Session
from enum import IntEnum

class BaseMixin:
    id = Column(Integer, primary_key=True, index=True, unique=True)
    created_at = Column(DateTime, nullable=False, default=func.utc_timestamp())
    updated_at = Column(DateTime, nullable=False, default=func.utc_timestamp(), onupdate=func.utc_timestamp())
    delected_at = Column(DateTime, nullable=False, default=func.utc_timestamp(), onupdate=func.utc_timestamp())
    
    def __init__(self):
        self._q = None
        self._session = None
        self.served = None

    def all_columns(self):
        return [c for c in self.__table__.columns if c.primary_key is False and c.name != "created_at"]

    def __hash__(self):
        return hash(self.id)

    @classmethod
    def create(cls, db: Session, auto_commit=False, **kwargs):
        """
        테이블 데이터 적재 전용 함수
        :param session:
        :param auto_commit: 자동 커밋 여부
        :param kwargs: 적재 할 데이터
        :return:
        """
        obj = cls()
        for col in obj.all_columns():
            col_name = col.name
            if col_name in kwargs:
                setattr(obj, col_name, kwargs.get(col_name))
        db.add(obj)
        db.flush()
        if auto_commit:
            db.commit()
        return obj

class Users(Base, BaseMixin):
    __tablename__ = 'users'
    login_id = Column(String(length=255), unique = True)
    login_pw = Column(String(length=255))
    login_name = Column(String(length=255))
    login_email = Column(String(length=255), unique = True)
    login_certification_number = Column(Integer) # 인증번호

    category = relationship(
        "Category",
        back_populates="users",
        cascade="all, delete",
        passive_deletes=True,
    )

    todo = relationship(
        "Todo",
        back_populates="users",
        cascade="all, delete",
        passive_deletes=True,
    )

    calendar = relationship(
        "Calendar",
        back_populates="users",
        cascade="all, delete",
        passive_deletes=True,
    )

    timeTracker = relationship(
        "TimeTracker",
        back_populates="users",
        cascade="all, delete",
        passive_deletes=True,
    )

    timeTrackerOrder = relationship(
        "TimeTrackerOrder",
        back_populates="users",
        cascade="all, delete",
        passive_deletes=True,
    )

    habit = relationship(
        "Habit",
        back_populates="users",
        cascade="all, delete",
        passive_deletes=True,
    )

    setting = relationship(
        "Setting",
        back_populates="users",
        cascade="all, delete",
        passive_deletes=True,
    )

class Category(Base, BaseMixin):
    __tablename__='category'
    user_id = Column(Integer, ForeignKey('users.id',ondelete="CASCADE"))
    name = Column(String(length=255), nullable=False) # todo ForeignKey
    color = Column(String(length=255), nullable=False)
    isTodo = Column(Integer, nullable=False)    # 0: time tracker 1: todo

    users = relationship("Users",back_populates="category")

class Todo(Base, BaseMixin):
    __tablename__ = 'todo'
    user_id = Column(Integer, ForeignKey('users.id',ondelete="CASCADE"))
    name = Column(String(length=255))
    date = Column(String(length=255))
    cName = Column(String(length=255)) # todo ForeignKey
    state = Column(Integer, default=0) # 0: 빈칸 1: 다음날 2: 안함 3: 체크

    users = relationship("Users",back_populates="todo")

class Calendar (Base, BaseMixin):
    __tablename__ = 'calendar'
    user_id = Column(Integer, ForeignKey('users.id',ondelete="CASCADE"))
    name = Column(String(length=255))
    color = Column(String(length=255))
    allDay = Column(Integer)
    startDate = Column(String(length=255))
    startTime = Column(String(length=255))
    endDate = Column(String(length=255))
    endTime = Column(String(length=255))
    location = Column(String(length=255))
    alarm = Column(Integer) # 0: 정각	1: 10분전	2:1시간전	3: 하루전
    alarmTime = Column(String(length=255))
    memo = Column(String(length=255))
    #요일 추가

    users = relationship("Users",back_populates="calendar")

class TimeTracker(Base, BaseMixin):
    __tablename__ = 'timeTracker'
    user_id = Column(Integer, ForeignKey('users.id',ondelete="CASCADE"))
    name = Column(String(length=255), nullable=False)
    today = Column(String(length=255))
    cName = Column(String(length=255)) 

    users = relationship("Users",back_populates="timeTracker")

class TimeTrackerOrder(Base, BaseMixin):
    __tablename__ = 'timeTrackerOrder'
    user_id = Column(Integer, ForeignKey('users.id',ondelete="CASCADE"))
    list_id = Column(Integer) 
    order = Column(Integer, nullable=False)
    startTime = Column(String(length=255))
    endTime = Column(String(length=255))
    timeTaken = Column(String(length=255))

    users = relationship("Users",back_populates="timeTrackerOrder")

class Habit(Base, BaseMixin):
    __tablename__ = 'habit'
    user_id = Column(Integer, ForeignKey('users.id',ondelete="CASCADE"))
    name = Column(String(length=255))
    today = Column(String(length=255))
    startDate = Column(String(length=255))
    endDate = Column(String(length=255))
    alarmSwitch = Column(Integer, default = 0)
    alarm = Column(String(length=255))
    repeatDay = Column(String(length=255)) # 일월화수목금토일
    repeatN = Column(Integer, default=0)
    habit_color = Column(String(length=255))
    habit_nfc = Column(String(length=255))
    habit_state = Column(Integer, default=0)   # 0: 빈칸 1: 체크
    dayOfWeek = Column(Integer) # 요일 추가

    users = relationship("Users",back_populates="habit")

class Setting(Base, BaseMixin):
    __tablename__ = 'setting'
    user_id = Column(Integer, ForeignKey('users.id',ondelete="CASCADE"))
    alarm_switch = Column(Integer, default=0)
    todo_time = Column(String(length=255))
    todo_switch = Column(Integer, default=0)
    habit_time = Column(String(length=255))
    habit_switch = Column(Integer, default=0)
    calendar_time = Column(String(length=255))
    calendar_switch = Column(Integer, default=0)
    time_switch = Column(Integer, default=0)
    dark_mode = Column(Integer, default=0)
    
    users = relationship("Users",back_populates="setting")