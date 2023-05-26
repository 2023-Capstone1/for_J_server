from xmlrpc.client import DateTime
from pydantic import BaseModel, EmailStr
from datetime import datetime

class Users(BaseModel):
    login_id: str
    login_pw: str
    login_name: str
    login_email: str
    login_certification_number: int

class Category(BaseModel):
    user_id: int
    name: str
    color: str
    isTodo: int

class Todo(BaseModel):
    user_id: int
    name: str
    date: str
    cName: str
    state: int

class Calendar (BaseModel):
    user_id: int
    name: str
    color: str
    allDay: int
    startDate: str
    startTime: str
    endDate: str
    endTime: str
    location: str
    alarm: int
    alarmTime: str
    memo: str

class TimeTracker(BaseModel):
    user_id: int
    name: str
    today: str
    cName: str

class TimeTrackerOrder(BaseModel):
    user_id: int
    list_id: int
    order: int
    startTime: str
    endTime: str
    timeTaken: str

class Habit(BaseModel):
    user_id: int
    name: str
    today: str
    startDate: str
    endDate: str
    alarmSwitch: int
    alarm: str
    repeatDay: str
    repeatN: int
    habit_color: str
    habit_nfc: str
    habit_state: int
    dayOfWeek: int

class Setting(BaseModel):
    user_id: int
    alarm_switch: int
    todo_time: str
    todo_switch: int
    habit_time: str
    habit_switch: int
    calendar_time: str
    calendar_switch: int
    time_switch: int
    dark_mode: int