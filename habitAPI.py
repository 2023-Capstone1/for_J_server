from fastapi import APIRouter, FastAPI, HTTPException
from requests import Session
from fastapi.params import Depends
from sqlalchemy import desc
from db import get_db
from pydantic import BaseModel

import models, statusCode
from datetime import datetime, timedelta
import json

router = APIRouter(prefix="/habitAPI",tags=["habitAPI"])

# 디비에 정보 저장하는 함수
def create_habit(db, user_id, name, today, startDate, endDate, alarmSwitch, alarm, repeatDay, repeatN, habit_color, habit_nfc, habit_state, dayOfWeek):
    if alarmSwitch == 0 and repeatN >= 1:
        models.Habit.create(db, auto_commit = True, user_id = user_id, name = name, 
                        today = today, startDate = startDate, endDate = endDate, 
                        alarmSwitch = alarmSwitch, alarm = "null", repeatDay = "null", repeatN = repeatN, 
                        habit_color = habit_color, habit_nfc = habit_nfc, habit_state = habit_state, dayOfWeek = dayOfWeek)
    # alarmSwitch가 0일 때 habit_alarm은 null으로
    elif alarmSwitch == 0:
        models.Habit.create(db, auto_commit = True, user_id = user_id, name = name, 
                        today = today, startDate = startDate, endDate = endDate, 
                        alarmSwitch = alarmSwitch, alarm = "null", repeatDay = repeatDay, repeatN = repeatN, 
                        habit_color = habit_color, habit_nfc = habit_nfc, habit_state = habit_state, dayOfWeek = dayOfWeek)
    # repeatN이 1 이상일 때 repeatDay는 null으로
    elif repeatN >= 1:
        models.Habit.create(db, auto_commit = True, user_id = user_id, name = name, 
                        today = today, startDate = startDate, endDate = endDate, 
                        alarmSwitch = alarmSwitch, alarm = alarm, repeatDay = "null", repeatN = repeatN, 
                        habit_color = habit_color, habit_nfc = habit_nfc, habit_state = habit_state, dayOfWeek = dayOfWeek)  
    else:
        models.Habit.create(db, auto_commit = True, user_id = user_id, name = name, 
                        today = today, startDate = startDate, endDate = endDate, 
                        alarmSwitch = alarmSwitch, alarm = alarm, repeatDay = repeatDay, repeatN = repeatN, 
                        habit_color = habit_color, habit_nfc = habit_nfc, habit_state = habit_state, dayOfWeek = dayOfWeek) 

# 해빗 최초 저장 메소드
@router.post("/set_habit/{login_id}/{name}/{startDate}/{endDate}/{alarmSwitch}/{alarm}/{repeatDay}/{repeatN}/{habit_color}/{habit_nfc}/{habit_state}",status_code=200)
async def set_habit(login_id: str, name: str, startDate:str, endDate:str, 
                    alarmSwitch:int, alarm:str, repeatDay:str, repeatN:int, 
                    habit_color:str, habit_nfc:str, habit_state:int, db:Session = Depends(get_db)):
    """
    해빗 리스트 생성 API
    """
    is_exist_userId = db.query(models.Users.id).filter_by(login_id=login_id).first()

    if is_exist_userId == None:
        return statusCode.no_exist_user
    elif login_id == None:
        return statusCode.not_id
    elif startDate == None:
        return statusCode.not_habit_startDate
    elif endDate == None:
        return statusCode.not_habit_endDate
    elif alarmSwitch == None:
        return statusCode.not_habit_alarmSwitch
    elif alarm == None:
        return statusCode.not_habit_alarm
    elif repeatDay == None:
        return statusCode.not_habit_repeatDay
    elif repeatN == None:
        return statusCode.not_habit_repeatN
    elif habit_color == None:
        return statusCode.not_habit_habit_color
    elif habit_nfc == None:
        return statusCode.not_habit_habit_nfc
    elif habit_state == None:
        return statusCode.not_habit_habit_state
    elif is_exist_userId:
        # 종료 날짜 ~ 시작 날짜 차이 계산
        between_days = datetime.strptime(endDate, '%Y-%m-%d') - datetime.strptime(startDate, '%Y-%m-%d') 
        if str(between_days) == "0:00:00": # 당일일 떄
            between_days = 0
        else:
            between_days = int(str(between_days).split(" ")[0]) # 기존 시작 날짜와 변경 시작 날짜 차이를 int형으로 저장
        
        # 종료 날짜 ~ 시작 날짜 사이의 반복 주기 요일 리스트 생성
        for i in range(0, between_days+1):
            new_date_to_create = datetime.strptime(startDate, '%Y-%m-%d') + timedelta(days=i) 
            if (repeatN > 0): # 반복 주기 1 이상일 때
                date = str(new_date_to_create).split(' ')[0] 
                create_habit(db, is_exist_userId.id, name, date, startDate, endDate, alarmSwitch, alarm, repeatDay, repeatN, habit_color, habit_nfc, habit_state, new_date_to_create.weekday())
            else: # 반복 주기 0 일 때(요일로 설정 하는 경우(예: '월화수'))
                new_RepeatDay = strDay_to_intDay(repeatDay) # 요일을 숫자로 바꿈
                for i in range(0, len(new_RepeatDay)): # currentRepeatDay 크기만큼 리스트 생성
                    if new_date_to_create.weekday() == int(new_RepeatDay[i]):
                        date = str(new_date_to_create).split(' ')[0] 
                        create_habit(db, is_exist_userId.id, name, date, startDate, endDate, alarmSwitch, alarm, repeatDay, repeatN, habit_color, habit_nfc, habit_state, new_date_to_create.weekday())
        return statusCode.success
    else:
        return statusCode.unexpected_error

# 해빗 수정 시 받아오는 정보
@router.get("/get_habit_to_update/{login_id}/{list_id}",status_code=200)
async def get_habit_to_update(login_id: str, list_id:int, db:Session = Depends(get_db)):
    """
    수정할 해빗 리스트 불러오기 API
    """
    is_exist_userId = db.query(models.Users).filter_by(login_id=login_id).first()
    habit_list = db.query(models.Habit).filter_by(user_id = is_exist_userId.id, id = list_id).first()

    if is_exist_userId == None:
        return statusCode.no_exist_user
    elif habit_list == None:
        return statusCode.not_habit_list
    elif login_id == None:
        return statusCode.not_id
    elif habit_list:
        result_habit_list = {"habit_name":habit_list.name, "habit_today" : habit_list.today, "habit_startDate" : habit_list.startDate, 
                         "habit_endDate": habit_list.endDate, "habit_alarmSwitch": habit_list.alarmSwitch, "habit_alarm": habit_list.alarm,
                         "habit_repeatDay": habit_list.repeatDay, "habit_repeatN": habit_list.repeatN, "habit_color": habit_list.habit_color,
                         "habit_nfc": habit_list.habit_nfc, "habit_state": habit_list.habit_state, "dayOfWeek":habit_list.dayOfWeek, "SUCCESS": 200}
        return result_habit_list
    else:
        return statusCode.unexpected_error

# 해당 날짜의 해빗 리스트 불러오기 -> 예: 26일에 저장된 모든 해빗 리스트 불러오기
@router.get("/get_habit_today/{login_id}/{today}",status_code=200)
async def get_habit_today(login_id: str, today:str, db:Session = Depends(get_db)):
    """
    특정 날짜의 해빗 리스트 불러오기 API
    """
    is_exist_userId = db.query(models.Users.id).filter_by(login_id=login_id).first()
    habit_list = db.query(models.Habit).filter_by(user_id = is_exist_userId.id, today = today).all()
    
    result_habit_list = "{"

    if is_exist_userId == None:
        return statusCode.no_exist_user
    elif habit_list == None:
        return statusCode.not_habit_list
    elif today != today:
        return statusCode.not_equal_date
    elif login_id == None:
        return statusCode.not_id
    elif today == None:
        return statusCode.not_habit_today
    elif is_exist_userId:
        result_habit_list += "\"habit_today_total"+"\" : \""+ str(len(habit_list)) + "\", "
        for i in range(0,len(habit_list)):
            if i == len(habit_list)-1: # 마지막 줄이면 끝에 , 뺌
                result_habit_list += ("\"habit_list_id"+str(i) + "\":\"" + str(habit_list[i].id) + "\", " 
                                      +"\"habit_name"+str(i)+"\" : \""+ habit_list[i].name + "\", "
                                      +"\"habit_today"+str(i)+"\" : \""+ habit_list[i].today + "\", "
                                      +"\"habit_startDate"+str(i)+"\" : \""+ habit_list[i].startDate + "\", "
                                      +"\"habit_endDate"+str(i)+"\" : \""+ habit_list[i].endDate + "\", "
                                      +"\"habit_alarmSwitch"+str(i)+"\" : \""+ str(habit_list[i].alarmSwitch) + "\", "
                                      +"\"habit_alarm"+str(i)+"\" : \""+ habit_list[i].alarm + "\", "
                                      +"\"habit_repeatDay"+str(i)+"\" : \""+ habit_list[i].repeatDay +"\", "
                                      +"\"habit_repeatN"+str(i)+"\" : \""+ str(habit_list[i].repeatN) +"\", "
                                      +"\"habit_color"+str(i)+"\" : \""+ habit_list[i].habit_color +"\", "
                                      +"\"habit_nfc"+str(i)+"\" : \""+ str(habit_list[i].habit_nfc) +"\", "
                                      +"\"habit_state"+str(i)+"\" : \""+ str(habit_list[i].habit_state) +"\", " 
                                      +"\"habit_dayOfWeek"+str(i)+"\" : \""+ str(habit_list[i].dayOfWeek) +"\", "+"\"SUCCESS"+"\" : \""+ str(200) +"\"")
            else: # 마지막 줄이 아니면 , 추가
                result_habit_list += ("\"habit_list_id"+str(i) + "\":\"" + str(habit_list[i].id) + "\", " 
                                      +"\"habit_name"+str(i)+"\" : \""+ habit_list[i].name + "\", "
                                      +"\"habit_today"+str(i)+"\" : \""+ habit_list[i].today + "\", "
                                      +"\"habit_startDate"+str(i)+"\" : \""+ habit_list[i].startDate + "\", "
                                      +"\"habit_endDate"+str(i)+"\" : \""+ habit_list[i].endDate + "\", "
                                      +"\"habit_alarmSwitch"+str(i)+"\" : \""+ str(habit_list[i].alarmSwitch) + "\", "
                                      +"\"habit_alarm"+str(i)+"\" : \""+ habit_list[i].alarm + "\", "
                                      +"\"habit_repeatDay"+str(i)+"\" : \""+ habit_list[i].repeatDay +"\", "
                                      +"\"habit_repeatN"+str(i)+"\" : \""+ str(habit_list[i].repeatN) +"\", "
                                      +"\"habit_color"+str(i)+"\" : \""+ habit_list[i].habit_color +"\", "
                                      +"\"habit_nfc"+str(i)+"\" : \""+ str(habit_list[i].habit_nfc) +"\", "
                                      +"\"habit_state"+str(i)+"\" : \""+ str(habit_list[i].habit_state) +"\", " 
                                      +"\"habit_dayOfWeek"+str(i)+"\" : \""+ str(habit_list[i].dayOfWeek) +"\", ")
        result_habit_list += "}"
        return json.loads(result_habit_list)
    else:
        return statusCode.unexpected_error

# 해빗 이름, 시작 날짜, 끝 날짜 같은 거 다 받아오기
# repeatN이 1 이상일 때만 호출
@router.get("/get_habit_same_name/{login_id}/{name}/{startDate}/{endDate}",status_code=200)
async def get_habit_same_name(login_id: str, name:str, startDate:str, endDate:str, db:Session = Depends(get_db)):
    """
    이름, 시작 날짜, 끝 날짜 같은 해빗 리스트 불러오기 API
    """
    is_exist_userId = db.query(models.Users.id).filter_by(login_id=login_id).first()
    habit_list_same_name = db.query(models.Habit).filter_by(user_id = is_exist_userId.id, name = name, startDate = startDate, endDate = endDate).all()
    
    result_habit_list = "{"

    if is_exist_userId == None:
        return statusCode.no_exist_user
    elif habit_list_same_name == None:
        return statusCode.not_habit_list
    elif login_id == None:
        return statusCode.not_id
    elif is_exist_userId and habit_list_same_name:
        result_habit_list += "\"habit_today_total"+"\" : \""+ str(len(habit_list_same_name)) + "\", "
        for i in range(0,len(habit_list_same_name)):
            if i == len(habit_list_same_name)-1: # 마지막 줄이면 끝에 , 뺌
                result_habit_list += ("\"habit_list_id"+str(i) + "\":\"" + str(habit_list_same_name[i].id) + "\", " 
                                      +"\"habit_name"+str(i)+"\" : \""+ habit_list_same_name[i].name + "\", "
                                      +"\"habit_today"+str(i)+"\" : \""+ habit_list_same_name[i].today + "\", "
                                      +"\"habit_startDate"+str(i)+"\" : \""+ habit_list_same_name[i].startDate + "\", "
                                      +"\"habit_endDate"+str(i)+"\" : \""+ habit_list_same_name[i].endDate + "\", "
                                      +"\"habit_alarmSwitch"+str(i)+"\" : \""+ str(habit_list_same_name[i].alarmSwitch) + "\", "
                                      +"\"habit_alarm"+str(i)+"\" : \""+ habit_list_same_name[i].alarm + "\", "
                                      +"\"habit_repeatDay"+str(i)+"\" : \""+ habit_list_same_name[i].repeatDay +"\", "
                                      +"\"habit_repeatN"+str(i)+"\" : \""+ str(habit_list_same_name[i].repeatN) +"\", "
                                      +"\"habit_color"+str(i)+"\" : \""+ habit_list_same_name[i].habit_color +"\", "
                                      +"\"habit_nfc"+str(i)+"\" : \""+ str(habit_list_same_name[i].habit_nfc) +"\", "
                                      +"\"habit_state"+str(i)+"\" : \""+ str(habit_list_same_name[i].habit_state) +"\", " 
                                      +"\"habit_dayOfWeek"+str(i)+"\" : \""+ str(habit_list_same_name[i].dayOfWeek) +"\", " +"\"SUCCESS"+"\" : \""+ str(200) +"\"")
            else: # 마지막 줄이 아니면 , 추가
                result_habit_list += ("\"habit_list_id"+str(i) + "\":\"" + str(habit_list_same_name[i].id) + "\", " 
                                      +"\"habit_name"+str(i)+"\" : \""+ habit_list_same_name[i].name + "\", "
                                      +"\"habit_today"+str(i)+"\" : \""+ habit_list_same_name[i].today + "\", "
                                      +"\"habit_startDate"+str(i)+"\" : \""+ habit_list_same_name[i].startDate + "\", "
                                      +"\"habit_endDate"+str(i)+"\" : \""+ habit_list_same_name[i].endDate + "\", "
                                      +"\"habit_alarmSwitch"+str(i)+"\" : \""+ str(habit_list_same_name[i].alarmSwitch) + "\", "
                                      +"\"habit_alarm"+str(i)+"\" : \""+ habit_list_same_name[i].alarm + "\", "
                                      +"\"habit_repeatDay"+str(i)+"\" : \""+ habit_list_same_name[i].repeatDay +"\", "
                                      +"\"habit_repeatN"+str(i)+"\" : \""+ str(habit_list_same_name[i].repeatN) +"\", "
                                      +"\"habit_color"+str(i)+"\" : \""+ habit_list_same_name[i].habit_color +"\", "
                                      +"\"habit_nfc"+str(i)+"\" : \""+ str(habit_list_same_name[i].habit_nfc) +"\", "
                                      +"\"habit_state"+str(i)+"\" : \""+ str(habit_list_same_name[i].habit_state) +"\", "
                                      +"\"habit_dayOfWeek"+str(i)+"\" : \""+ str(habit_list_same_name[i].dayOfWeek) +"\", ")
        result_habit_list += "}"
        return json.loads(result_habit_list)
    else:
        return statusCode.unexpected_error  

# habit 삭제 
@router.delete("/habit_delete/{login_id}/{name}/{startDate}/{endDate}/{today}",status_code=200)
async def habit_delete(login_id: str, name:str, startDate:str, endDate:str, today:str, db:Session = Depends(get_db)):
    """
    해빗 삭제 API
    """
    exist_user_id = db.query(models.Users.id).filter_by(login_id = login_id).first()
    exist_habit = db.query(models.Habit).filter_by(user_id = exist_user_id.id, name=name, startDate=startDate, endDate=endDate, today=today).first()

    if exist_user_id == None:
        return statusCode.no_exist_user
    elif exist_user_id and exist_habit: 
        db.query(models.Habit).filter_by(user_id = exist_user_id.id, name=name, startDate=startDate, endDate=endDate, today=today).delete()
        db.commit()
        return statusCode.success
    elif None == exist_user_id: # login_id가 없는 경우
        return statusCode.not_id
    elif None == exist_habit: # 해당 조건에 대한 habit_id가 없는 경우
        return statusCode.none_correction_data    
    else:
        return statusCode.unexpected_error

# habit 삭제 -list_id 이용
@router.delete("/habit_delete_with_id/{login_id}/{list_id}",status_code=200)
async def habit_delete_with_id(login_id: str, list_id:int, db:Session = Depends(get_db)):
    """
    해빗 삭제(list_id 사용) API
    """
    exist_user_id = db.query(models.Users.id).filter_by(login_id = login_id).first()
    exist_habit = db.query(models.Habit).filter_by(user_id = exist_user_id.id, id=list_id).first()

    if exist_user_id == None:
        return statusCode.no_exist_user
    elif exist_user_id and exist_habit: 
        db.query(models.Habit).filter_by(user_id = exist_user_id.id, id=list_id).delete()
        db.commit()
        return statusCode.success
    elif None == exist_user_id: # login_id가 없는 경우
        return statusCode.not_id
    elif None == exist_habit: # 해당 조건에 대한 habit_id가 없는 경우
        return statusCode.none_correction_data    
    else:
        return statusCode.unexpected_error        

@router.get("/get_habit_state/{login_id}/{list_id}/{name}/{date}",status_code=200)
async def get_habit_state(login_id: str, list_id:int, name: str, date: str, db:Session = Depends(get_db)):
    """"
    해빗 리스트의 상태 가져오기 API
    """
    is_exist_userId = db.query(models.Users.id).filter_by(login_id = login_id).first()
    habit_list = db.query(models.Habit).filter_by(user_id = is_exist_userId.id, name=name, today=date, id=list_id).first()

    result_todo_list = {"habit_state": habit_list.habit_state, "SUCCESS": 200}

    if is_exist_userId == None:
        return statusCode.no_exist_user
    elif habit_list.name == name and habit_list.today == date: # 리스트 이름이랑 리스트의 날짜가 모두 같을 때
        return result_todo_list # 값 리턴
    elif is_exist_userId == None:
        return statusCode.not_id
    elif habit_list == None: 
        return statusCode.no_exist_todo_list
    elif habit_list.name == None: 
        return statusCode.not_todo_name
    elif habit_list.today == None: 
        return statusCode.not_todo_date
    else :
        return statusCode.unexpected_error

# nfc 상태 업데이트 -nfc 값이 동일한 habit 리스트의 상태(완료/미완료) 업데이트
@router.put("/update_habit_state/{login_id}/{today}/{nfc}",status_code=200)
async def update_habit_state(login_id: str, today:str, nfc: str, db:Session = Depends(get_db)):
    """
    nfc 태그 시 habit 리스트의 상태를 수정하는 API
    """
    is_exist_userId = db.query(models.Users.id).filter_by(login_id=login_id).first()
    get_nfc = db.query(models.Habit.habit_nfc).filter_by(user_id=is_exist_userId.id, today=today, habit_nfc=nfc).first()

    if is_exist_userId and get_nfc:
        db.query(models.Habit).filter(models.Habit.user_id == is_exist_userId.id).update({"habit_state":1})
        db.commit()
        return statusCode.success
    elif get_nfc == None:
        return statusCode.not_habit_habit_nfc
    elif is_exist_userId == None:
        return statusCode.not_id
    return statusCode.unexpected_error

# 여기부터는 해빗 업데이트 메소드용
# 스트링으로 받은 repeatDay를 int로 바꾸는 함수 만들어서 쓰기 (월 -> 0으로 변경)
def strDay_to_intDay(repeatDay:str):
    # 월화수목금토일 -> 0123456 으로 바꾸는 함수 reutn은 str그대로 문자 교체만 진행
    new_repeatDay = ""
    for i in range(0, len(repeatDay)):
        if (repeatDay[i]) == '월':
            new_repeatDay += '0'
        elif (repeatDay[i]) == '화':
            new_repeatDay += '1'
        elif (repeatDay[i]) == '수':
            new_repeatDay += '2'
        elif (repeatDay[i]) == '목':
            new_repeatDay += '3'
        elif (repeatDay[i]) == '금':
            new_repeatDay += '4'
        elif (repeatDay[i]) == '토':
            new_repeatDay += '5'
        elif (repeatDay[i]) == '일':
            new_repeatDay += '6'

    return new_repeatDay    

@router.put("/update_habit/{login_id}/{preName}/{currentName}/{preStartDate}/{currentStartDate}/{preEndDate}/{currentEndDate}/{currentAlarmSwitch}/{currentAlarm}/{currentRepeatDay}/{currentRepeatN}/{currentHabit_color}/{currentHabit_nfc}/{currentHabit_state}",status_code=200) #서버로 보내야하는 값 + 안드로이드에서 보낸 값(메소드에서 그 값 사용가능)
async def update_habit(login_id: str, preName:str, currentName:str, preStartDate:str, currentStartDate:str, preEndDate:str, 
                          currentEndDate:str, currentAlarmSwitch:int, currentAlarm:str, currentRepeatDay:str, currentRepeatN:int, 
                          currentHabit_color:str, currentHabit_nfc:str, currentHabit_state:int ,db:Session = Depends(get_db)): #서버 홈페이지에서 값을 입력하는 칸
    """
    해빗 업데이트 API
    """
    is_exist_userId = db.query(models.Users).filter_by(login_id=login_id).first()
    # preData 사용 -> 기존에 있는 튜플 확인해서 다 지울 것들
    habit_list = db.query(models.Habit).filter_by(user_id = is_exist_userId.id, name=preName, startDate=preStartDate, endDate=preEndDate, habit_state=currentHabit_state).all()
    
    if is_exist_userId == None:
        return statusCode.no_exist_user
    elif habit_list == None:
        return statusCode.not_habit_list
    elif habit_list and (currentRepeatN > 0):
        for i in range(0, len(habit_list)):
            db.delete(habit_list[i])
            db.commit()

        # 변경 종료 날짜 ~ 변경 시작 날짜 사이 개수 찾기
        between_days = datetime.strptime(currentEndDate, '%Y-%m-%d') - datetime.strptime(currentStartDate, '%Y-%m-%d') 
        between_days = int(str(between_days).split(" ")[0]) # 기존 시작 날짜와 변경 시작 날짜 차이를 int형으로 저장
        
        # 변경 종료 날짜 ~ 변경 시작 날짜 사이 리스트 모두 생성 (today는 일단 None으로) 
        for i in range(0, between_days+1):
            new_date_to_create = datetime.strptime(currentStartDate, '%Y-%m-%d') + timedelta(days=i) 
            date = str(new_date_to_create).split(' ')[0] 
            create_habit(db, is_exist_userId.id, currentName, date, currentStartDate, currentEndDate, currentAlarmSwitch, currentAlarm, 
                         currentRepeatDay, currentRepeatN, currentHabit_color, currentHabit_nfc, currentHabit_state, new_date_to_create.weekday())
        return statusCode.success

    elif habit_list and (currentRepeatN == 0): #직접 지정 월수금 currentRepeatDay

        new_currentRepeatDay = strDay_to_intDay(currentRepeatDay) # 요일을 숫자로 바꿈

        for i in range(0, len(habit_list)):
            db.delete(habit_list[i])
            db.commit()

        # 변경 종료 날짜 ~ 변경 시작 날짜 사이 개수 찾기
        between_days = datetime.strptime(currentEndDate, '%Y-%m-%d') - datetime.strptime(currentStartDate, '%Y-%m-%d') 
        between_days = int(str(between_days).split(" ")[0]) # 기존 시작 날짜와 변경 시작 날짜 차이를 int형으로 저장
        
        # 변경 종료 날짜 ~ 변경 시작 날짜 사이의 반복 주기 요일 리스트 생성
        for i in range(0, between_days+1):
            new_date_to_create = datetime.strptime(currentStartDate, '%Y-%m-%d') + timedelta(days=i) 
            for i in range(0, len(new_currentRepeatDay)): # currentRepeatDay 크기만큼 리스트 생성
                if new_date_to_create.weekday() == int(new_currentRepeatDay[i]):
                    date = str(new_date_to_create).split(' ')[0] 
                    create_habit(db, is_exist_userId.id, currentName, date, currentStartDate, currentEndDate, currentAlarmSwitch, currentAlarm, 
                                 currentRepeatDay, currentRepeatN, currentHabit_color, currentHabit_nfc, currentHabit_state, new_date_to_create.weekday())
        return statusCode.success 

    else:
        return statusCode.unexpected_error