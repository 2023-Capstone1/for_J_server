from fastapi import APIRouter, FastAPI, HTTPException
from requests import Session
from fastapi.params import Depends
from sqlalchemy import desc
from db import get_db
from pydantic import BaseModel

import models, datetime, random, statusCode
from datetime import datetime, timedelta, time
import json

router = APIRouter(prefix="/checkAPI",tags=["checkAPI"])
    
# nfc가 있는 모든 테이블에서 nfc 씨리얼번호 중복되는지 확인하는 메소드 --> habit, time 하나로 묶음 -> nfcAPI 로 따로?
@router.get("/get_is_nfc_exist/{login_id}/{table_name}/{nfc}",status_code=200)
async def get_is_nfc_exist(login_id: str, table_name:str, nfc: str, db:Session = Depends(get_db)):
    """
    nfc 씨리얼번호 중복 확인하는 메소드
    """
    is_exist_userId = db.query(models.Users.id).filter_by(login_id=login_id).first()
    if (table_name == "habit"):
        nfc_exist = db.query(models.Habit.habit_nfc).filter_by(user_id = is_exist_userId.id, habit_nfc=nfc).first() # nfc 값이 일치하면 값이 생김
    elif (table_name == "time"):
        nfc_exist = db.query(models.Habit.habit_nfc).filter_by(user_id = is_exist_userId.id, habit_nfc=nfc).first() # nfc 값이 일치하면 값이 생김
    
    if is_exist_userId == None:
        return statusCode.no_exist_users
    elif is_exist_userId and nfc_exist: # nfc_exist 값이 존재하면 중복(1) 리턴
        is_nfc_exist_result = {"is_nfc_exist": 1, "SUCCESS": 200}
        return is_nfc_exist_result
    elif is_exist_userId and nfc_exist == None: # nfc_exist 값이 없고 로그인 아이디는 존재할 때 중복아님(0) 리턴
        is_nfc_exist_result = {"is_nfc_exist": 0, "SUCCESS": 200}
        return is_nfc_exist_result
    else:
        return statusCode.unexpected_error

# calendar 리스트 존재 여부 파악하는 함수
def is_tuple_exist_calendar(login_id, db, date):
    datetime_date = datetime.strptime(date, '%Y-%m-%d')
    is_tuple_check = 0 # 리스트 존재 여부 파악

    exist_user_id = db.query(models.Users).filter_by(login_id = login_id).first()
    is_exist_cal = db.query(models.Calendar).filter_by(user_id = exist_user_id.id).all()

    for i in range(0, len(is_exist_cal)):
        check_startDate = datetime.strptime(is_exist_cal[i].startDate, '%Y-%m-%d') # 시작 날짜
        check_endDate = datetime.strptime(is_exist_cal[i].endDate, '%Y-%m-%d') # 끝 날짜

        if ((check_startDate <= datetime_date) and (check_endDate >= datetime_date)): # 매개변수로 보내준 날짜와 시작 날짜, 끝 날짜 비교
            is_tuple_check += 1

    if (is_tuple_check > 0):
        return {"is_tuple_exist": 1, "SUCCESS": 200}

# 특정 날짜에 리스트가 있는지 없는지 확인하는 메소드 -Todo, Calendar, TimeTracker, Habit
@router.get("/get_is_tuple_exist/{login_id}/{table_name}/{date}", status_code=200)
async def get_is_tuple_exist(login_id:str, table_name:str, date:str, db:Session=Depends(get_db)):
    """
    튜플 존재 여부 확인 API -table_name은 todo, habit, calendar, time으로 넘겨주면 됨
    """
    exist_user_id = db.query(models.Users.id).filter_by(login_id = login_id).first()
    
    if table_name == "todo":
        check_tuple = db.query(models.Todo).filter_by(user_id = exist_user_id.id, date=date).first()
    elif table_name == "habit":
        check_tuple = db.query(models.Habit).filter_by(user_id = exist_user_id.id, today=date).first()
    elif table_name == "calendar":
        check_tuple = is_tuple_exist_calendar(login_id, db, date)
    elif table_name == "time":
        check_tuple = db.query(models.TimeTracker).filter_by(user_id = exist_user_id.id, today=date).first()

    if exist_user_id == None:
        return statusCode.no_exist_user
    elif check_tuple == None: # 튜플이 존재하지 않음
        return {"is_tuple_exist": 0, "SUCCESS": 200}
    elif check_tuple: # 튜플 존재함
        return {"is_tuple_exist": 1, "SUCCESS": 200}

