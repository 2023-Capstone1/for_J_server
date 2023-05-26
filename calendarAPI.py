from fastapi import APIRouter, FastAPI, HTTPException
from requests import Session
from fastapi.params import Depends
from db import get_db

import models, statusCode, json
from datetime import datetime, timedelta, time

router = APIRouter(prefix="/calendarAPI",tags=["calendarAPI"])

@router.post("/set_calendar/{login_id}/{name}/{color}/{allDay}/{startDate}/{startTime}/{endDate}/{endTime}/{location}/{alarm}/{memo}",status_code=200)
async def set_calendar(login_id: str, name: str, color: str, allDay: int, startDate: str, startTime: str, endDate: str, endTime: str, location: str, alarm: int, memo: str, db:Session = Depends(get_db)):
    """
    캘린더 리스트 생성 API
    """
    is_exist_user = db.query(models.Users).filter_by(login_id=login_id).first()

    if is_exist_user == None:
        return statusCode.no_exist_user
    elif name == None:
        return statusCode.no_cal_name
    elif color == None:
        return statusCode.no_cal_color
    elif allDay == None:
        return statusCode.no_cal_allday
    elif startDate == None:
        return statusCode.no_cal_startDate
    elif startTime == None:
        return statusCode.no_cal_startTime
    elif endDate == None:
        return statusCode.no_cal_endDate
    elif endTime == None:
        return statusCode.no_cal_endTime
    elif location == None:
        return statusCode.no_cal_location
    elif alarm == None:
        return statusCode.no_cal_alarm
    elif memo == None:
        return statusCode.no_cal_memo
    elif login_id:
        # allDay == 1이면 아래는 실행 x + alarmTime에 "null" 넣기
        if allDay == 0:
            if alarm == 0: # 설정된 시간
                models.Calendar.create(db, auto_commit = True, user_id = is_exist_user.id, name = name, color = color, 
                                        allDay = allDay, startDate = startDate, startTime = startTime, endDate = endDate,
                                        endTime = endTime, location = location, alarm = alarm, alarmTime = startTime, memo = memo)
                return statusCode.success            
            elif alarm == 1: # 10분전
                start_detetime = datetime.strptime(startTime, "%H:%M")
                modified_dateTime = start_detetime - timedelta(minutes=10)
                modified_time_str = modified_dateTime.strftime("%H:%M")
                result_alarmTime = startDate + " " + modified_time_str
                
                models.Calendar.create(db, auto_commit = True, user_id = is_exist_user.id, name = name, color = color, 
                                        allDay = allDay, startDate = startDate, startTime = startTime, endDate = endDate,
                                        endTime = endTime, location = location, alarm = alarm, alarmTime = result_alarmTime, memo = memo)
                return statusCode.success     
            elif alarm == 2: # 1시간전
                start_detetime = datetime.strptime(startTime, "%H:%M")
                modified_dateTime = start_detetime - timedelta(minutes=60)
                modified_time_str = modified_dateTime.strftime("%H:%M")
                result_alarmTime = startDate + " " + modified_time_str
                models.Calendar.create(db, auto_commit = True, user_id = is_exist_user.id, name = name, color = color, 
                                        allDay = allDay, startDate = startDate, startTime = startTime, endDate = endDate,
                                        endTime = endTime, location = location, alarm = alarm, alarmTime = result_alarmTime, memo = memo)
                return statusCode.success     
            elif alarm == 3: # 하루 전
                date_obj = datetime.strptime(startDate, "%Y-%m-%d")
                previous_date = date_obj - timedelta(days=1)
                start_time_str = previous_date.strftime("%Y-%m-%d")
                result_alarmTime = start_time_str + " " + startTime
                
                models.Calendar.create(db, auto_commit = True, user_id = is_exist_user.id, name = name, color = color, 
                                        allDay = allDay, startDate = startDate, startTime = startTime, endDate = endDate,
                                        endTime = endTime, location = location, alarm = alarm, alarmTime = result_alarmTime, memo = memo)
                return statusCode.success
        elif allDay == 1:
            models.Calendar.create(db, auto_commit = True, user_id = is_exist_user.id, name = name, color = color, 
                                        allDay = allDay, startDate = startDate, startTime = startTime, endDate = endDate,
                                        endTime = endTime, location = location, alarm = alarm, alarmTime = "null", memo = memo)
            return statusCode.success
    else:
        return statusCode.unexpected_error
    
# get_cal_list(login_id, today)
# - total, list_id(i), name(i), color(i), allDay(i), startDate(i), startTime(i), endDate(i), endTime(i), location(i), alarm(i), memo(i)
@router.get("/get_cal_list/{login_id}/{today}",status_code=200)
async def get_cal_list(login_id: str, today:str, db:Session = Depends(get_db)):
    """
    시작 날짜 ~ 종료 날짜 사이 일정 모두 보내주기 API
    """

    is_exist_userId = db.query(models.Users).filter_by(login_id=login_id).first()
    is_exist_cal = db.query(models.Calendar).filter_by(user_id = is_exist_userId.id).all()
    result_cal_list = "{"

    today_cal_total = 0 
    datetime_today = datetime.strptime(today, '%Y-%m-%d')
    j = 0
    for i in range(0, len(is_exist_cal)):   
        check_startDate = datetime.strptime(is_exist_cal[i].startDate, '%Y-%m-%d')
        check_endDate = datetime.strptime(is_exist_cal[i].endDate, '%Y-%m-%d')

        if ((check_startDate <= datetime_today) and (check_endDate >= datetime_today)):
            today_cal_total += 1
            result_cal_list += ("\"cal_list_id"+str(j) + "\":\"" + str(is_exist_cal[i].id) + "\", " +
                                "\"cal_list_name"+str(j) + "\":\"" + is_exist_cal[i].name + "\", " +
                                "\"cal_list_color"+str(j) + "\":\"" + is_exist_cal[i].color + "\", " +
                                "\"cal_list_allDay"+str(j) + "\":\"" + str(is_exist_cal[i].allDay) + "\", " +
                                "\"cal_list_startDate"+str(j) + "\":\"" + is_exist_cal[i].startDate + "\", " +
                                "\"cal_list_startTime"+str(j) + "\":\"" + is_exist_cal[i].startTime + "\", " +
                                "\"cal_list_endDate"+str(j) + "\":\"" + is_exist_cal[i].endDate + "\", " +
                                "\"cal_list_endTime"+str(j) + "\":\"" + is_exist_cal[i].endTime + "\", " +
                                "\"cal_list_location"+str(j) + "\":\"" + is_exist_cal[i].location + "\", " +
                                "\"cal_list_alarm"+str(j) + "\":\"" + str(is_exist_cal[i].alarm) + "\", " +
                                "\"cal_list_memo"+str(j) + "\":\"" + is_exist_cal[i].memo + "\", ")
            j += 1
    
    result_cal_list += "\"total"+"\" : \"" + str(today_cal_total) + "\", " + "\"SUCCESS"+"\" : \"" + str(200) + "\"" + "}"
    return json.loads(result_cal_list)

# #update_cal -> set_cal이랑 똑같지만, update로
@router.put("/update_cal/{login_id}/{list_id}/{name}/{color}/{allDay}/{startDate}/{startTime}/{endDate}/{endTime}/{location}/{alarm}/{memo}",status_code=200)
async def update_cal(login_id: str, list_id: int, name: str, color: str, allDay: int, startDate: str, startTime: str, endDate: str, endTime: str, location: str, alarm: int, memo: str, db:Session = Depends(get_db)):

    is_exist_user = db.query(models.Users).filter_by(login_id=login_id).first()
    update_list = db.query(models.Calendar).filter_by(user_id=is_exist_user.id, id=list_id).first()

    if is_exist_user == None:
        return statusCode.no_exist_user
    elif update_list == None:
        return statusCode.unexpected_error
    elif login_id == None:
        return statusCode.not_id
    elif color == None:
        return statusCode.no_cal_color
    elif allDay == None:
        return statusCode.no_cal_allday
    elif startDate == None:
        return statusCode.no_cal_startDate
    elif startTime == None:
        return statusCode.no_cal_startTime
    elif endDate == None:
        return statusCode.no_cal_endDate
    elif endTime == None:
        return statusCode.no_cal_endTime
    elif location == None:
        return statusCode.no_cal_location
    elif alarm == None:
        return statusCode.no_cal_alarm
    elif memo == None:
        return statusCode.no_cal_memo
    elif allDay == 1:
        if is_exist_user and update_list:
            update_list.name = name
            update_list.color = color
            update_list.allDay = allDay
            update_list.startDate = startDate
            update_list.startTime = startTime
            update_list.endDate = endDate
            update_list.endTime = endTime
            update_list.location = location
            update_list.alarm = alarm
            update_list.alarmTime = "null"
            update_list.memo = memo
            db.add(update_list)
            db.commit()
            return statusCode.success
    elif is_exist_user and update_list:
        if update_list and allDay == 0:
            if alarm == 0: # 설정된 시간
                update_list.name = name
                update_list.color = color
                update_list.allDay = allDay
                update_list.startDate = startDate
                update_list.startTime = startTime
                update_list.endDate = endDate
                update_list.endTime = endTime
                update_list.location = location
                update_list.alarm = alarm
                update_list.alarmTime = startTime
                update_list.memo = memo
                db.add(update_list)
                db.commit()
                return statusCode.success
            if alarm == 1: # 10분전
                start_detetime = datetime.strptime(startTime, "%H:%M")
                modified_dateTime = start_detetime - timedelta(minutes=10)
                modified_time_str = modified_dateTime.strftime("%H:%M")
                result_alarmTime = startDate + " " + modified_time_str

                update_list.name = name
                update_list.color = color
                update_list.allDay = allDay
                update_list.startDate = startDate
                update_list.startTime = startTime
                update_list.endDate = endDate
                update_list.endTime = endTime
                update_list.location = location
                update_list.alarm = alarm
                update_list.alarmTime = result_alarmTime
                update_list.memo = memo
                db.add(update_list)
                db.commit()
                return statusCode.success
            if alarm == 2: # 한시간 전
                start_detetime = datetime.strptime(startTime, "%H:%M")
                modified_dateTime = start_detetime - timedelta(minutes=60)
                modified_time_str = modified_dateTime.strftime("%H:%M")
                result_alarmTime = startDate + " " + modified_time_str

                update_list.name = name
                update_list.color = color
                update_list.allDay = allDay
                update_list.startDate = startDate
                update_list.startTime = startTime
                update_list.endDate = endDate
                update_list.endTime = endTime
                update_list.location = location
                update_list.alarm = alarm
                update_list.alarmTime = result_alarmTime
                update_list.memo = memo
                db.add(update_list)
                db.commit()
                return statusCode.success
            if alarm == 3: # 하루 전
                date_obj = datetime.strptime(startDate, "%Y-%m-%d")
                previous_date = date_obj - timedelta(days=1)
                start_time_str = previous_date.strftime("%Y-%m-%d")
                result_alarmTime = start_time_str + " " + startTime

                update_list.name = name
                update_list.color = color
                update_list.allDay = allDay
                update_list.startDate = startDate
                update_list.startTime = startTime
                update_list.endDate = endDate
                update_list.endTime = endTime
                update_list.location = location
                update_list.alarm = alarm
                update_list.alarmTime = result_alarmTime
                update_list.memo = memo
                db.add(update_list)
                db.commit()
                return statusCode.success
    else:
        return statusCode.unexpected_error
    
@router.get("/get_cal_to_update/{login_id}/{list_id}",status_code=200)
async def get_cal_to_update(login_id: str, list_id: int, db:Session = Depends(get_db)):
    """
    수정할 캘린더 리스트 불러오기 API
    """
    is_exist_userId = db.query(models.Users).filter_by(login_id=login_id).first()
    cal_list = db.query(models.Calendar).filter_by(user_id = is_exist_userId.id, id = list_id).first()

    result_cal_list = {"cal_list_id":cal_list.id, "cal_name":cal_list.name, "cal_color" : cal_list.color, "cal_allDay" : cal_list.allDay, "cal_startDate": cal_list.startDate, "cal_startTime": cal_list.startTime, "cal_endDate": cal_list.endDate, "cal_endTime": cal_list.endTime, "cal_location": cal_list.location, "cal_alarm": cal_list.alarm, "cal_alarmTime": cal_list.alarmTime, "cal_memo": cal_list.memo, "SUCCESS": 200}

    if is_exist_userId == None:
        return statusCode.no_exist_user
    elif cal_list == None:
        return statusCode.not_exist_cal_list
    elif login_id == None:
        return statusCode.not_id
    elif cal_list:
        return result_cal_list
    else:
        return statusCode.unexpected_error
    
    
@router.delete("/cal_delete/{login_id}/{list_id}",status_code=200)
async def cal_delete(login_id: str, list_id:int, db:Session = Depends(get_db)):
    """
    캘린더 삭제 API
    """
    exist_user_id = db.query(models.Users.id).filter_by(login_id = login_id).first()
    exist_cal = db.query(models.Calendar).filter_by(user_id = exist_user_id.id, id=list_id).first()

    if exist_user_id == None:
        return statusCode.no_exist_user
    elif exist_user_id and exist_cal: 
        db.query(models.Calendar).filter_by(user_id = exist_user_id.id, id=list_id).delete()
        db.commit()
        return statusCode.success
    elif None == exist_user_id: # login_id가 없는 경우
        return statusCode.not_id
    elif None == exist_cal: # 해당 조건에 대한 cal_id가 없는 경우
        return statusCode.none_correction_data    
    else:
        return statusCode.unexpected_error