from fastapi import APIRouter, FastAPI, HTTPException
from requests import Session
from fastapi.params import Depends
from db import get_db

import models, statusCode
from datetime import datetime, timedelta, time
import json

router = APIRouter(prefix="/timeAPI",tags=["timeAPI"])

# 타임트래커 리스트 정보 저장
@router.post("/set_timeTracker/{login_id}/{name}/{today}/{cName}",status_code=200)
async def set_timeTracker(login_id: str, name: str, today:str, cName:str,  db:Session = Depends(get_db)):
    """
    타임트래커 리스트 생성 API
    """
    is_exist_userId = db.query(models.Users).filter_by(login_id=login_id).first() # user_id=login_id => login_id=login_id 로 수정했음

    if is_exist_userId == None:
        return statusCode.no_exist_user
    elif login_id == None:
        return statusCode.not_id
    elif name == None:
        return statusCode.no_time_name
    elif today == None:
        return statusCode.no_time_today
    elif cName == None:
        return statusCode.no_time_cName
    elif is_exist_userId:
        models.TimeTracker.create(db, auto_commit = True, user_id = is_exist_userId.id, name = name, today = today, cName = cName)
        return statusCode.success
    else:
        return statusCode.unexpected_error

# 특정 날짜에 사용되는 카테고리 모두 반환
@router.get("/get_time_date_category/{login_id}/{today}/{isTodo}",status_code=200)
async def get_time_date_category(login_id: str, today: str, isTodo: int, db:Session = Depends(get_db)):
    """
    특정 날짜에서 사용되는 모든 타임 카테고리 값 확인 API
    """
    is_exist_userId = db.query(models.Users.id).filter_by(login_id = login_id).first()
    is_exist_TimeTracker_cName = db.query(models.TimeTracker.cName).filter_by(user_id = is_exist_userId.id, today = today).all()
    if isTodo == 1: # 타임쪽은 isTodo 0이어야함
        return statusCode.isTodo_error

    result_time_list = "{"
    
    if is_exist_userId == None:
        return statusCode.no_exist_user
    elif login_id == None:
        return statusCode.not_id
    elif today == None:
        return statusCode.not_todo_date  
    elif is_exist_TimeTracker_cName == None:
        return statusCode.no_exist_todo_list
    elif login_id and today and is_exist_TimeTracker_cName:
        result_time_list += "\"time_category_total"+"\" : \""+ str(len(is_exist_TimeTracker_cName)) + "\", "
        for i in range(0,len(is_exist_TimeTracker_cName)):
            is_exist_category_color = db.query(models.Category).filter_by(user_id = is_exist_userId.id, name = is_exist_TimeTracker_cName[i].cName).first() # 투두 카테고리 색상도 같이 보내주기 위함
            if i == len(is_exist_TimeTracker_cName)-1: # 마지막 줄이면 끝에 , 뺌
                result_time_list += "\"time_cName"+str(i)+"\" : \""+ is_exist_TimeTracker_cName[i].cName + "\", " + "\"time_cColor"+str(i)+"\" : \""+ is_exist_category_color.color + "\", " + "\"SUCCESS"+"\" : \"" + str(200) + "\""
            else: # 마지막 줄이 아니면 , 추가
                result_time_list += "\"time_cName"+str(i)+"\" : \""+ is_exist_TimeTracker_cName[i].cName + "\", " + "\"time_cColor"+str(i)+"\" : \""+ is_exist_category_color.color + "\", "
        result_time_list += "}"
        return json.loads(result_time_list)
    else:
        return statusCode.unexpected_error

# 날짜 리스트 값 반환 (예: 2023-05-08인 타임 리스트 반환)
@router.get("/get_time_list/{login_id}/{today}",status_code=200)
async def get_time_list(login_id: str, today:str, db:Session = Depends(get_db)):
    """
    특정 날짜의 모든 타임 리스트 값 확인 API
    """
    is_exist_userId = db.query(models.Users.id).filter_by(login_id=login_id).first()
    is_exist_time = db.query(models.TimeTracker).filter_by(user_id = is_exist_userId.id, today = today).all()

    result_time_list = "{"
    
    if is_exist_userId == None:
        return statusCode.no_exist_user
    elif login_id == None:
        return statusCode.not_id
    elif today == None:
        return statusCode.not_todo_date
    elif is_exist_time == None:
        return statusCode.no_exist_time_list
    elif login_id and today and is_exist_time:
        result_time_list += "\"time_total"+"\" : \""+ str(len(is_exist_time)) + "\", "
        for i in range(0,len(is_exist_time)):
            if i == len(is_exist_time)-1: # 마지막 줄이면 끝에 , 뺌
                result_time_list += ("\"time_list_id"+str(i) + "\":\"" + str(is_exist_time[i].id) + "\", " 
                                    + "\"time_name"+str(i)+"\" : \""+ is_exist_time[i].name + "\", " 
                                    + "\"time_cName"+str(i)+"\" : \"" + is_exist_time[i].cName +"\", " 
                                    + "\"SUCCESS"+"\" : \"" + str(200) + "\"")
            else: # 마지막 줄이 아니면 , 추가
                result_time_list += ("\"time_list_id"+str(i) + "\":\"" + str(is_exist_time[i].id) + "\", " 
                                    + "\"time_name"+str(i)+"\" : \""+ is_exist_time[i].name + "\", " 
                                    +"\"time_cName"+str(i)+"\" : \""+ is_exist_time[i].cName +"\", ")
        result_time_list += "}"
        return json.loads(result_time_list)
    else:
        return statusCode.unexpected_error

@router.get("/get_time_to_update/{login_id}/{list_id}",status_code=200)
async def get_time_to_update(login_id: str, list_id:int, db:Session = Depends(get_db)):
    """
    타임 리스트 값 한 개 확인 API
    """
    is_exist_userId = db.query(models.Users.id).filter_by(login_id=login_id).first()
    time_list = db.query(models.TimeTracker).filter_by(user_id = is_exist_userId.id, id=list_id).first()

    result_time_list = {"time_list_id":time_list.id, "time_name":time_list.name, "time_today" : time_list.today, "time_cName" : time_list.cName, "SUCCESS": 200}

    if is_exist_userId == None:
        return statusCode.no_exist_user
    elif login_id == None:
        return statusCode.not_id
    elif list_id == None:
        return statusCode.no_list_id    
    elif time_list == None:
        return statusCode.no_exist_todo_list
    elif login_id and list_id:
        return result_time_list
    else:
        return statusCode.unexpected_error

# 타임 리스트 수정
@router.put("/update_time/{login_id}/{list_id}/{name}/{today}/{cName}",status_code=200)
async def update_time(login_id: str, list_id:int, name: str, today:str, cName:str, db:Session = Depends(get_db)):
    """
    타임 리스트 수정 API
    """
    is_exist_userId = db.query(models.Users).filter_by(login_id=login_id).first()

    update_data = db.query(models.TimeTracker).filter_by(user_id=is_exist_userId.id, id=list_id).first()
    
    if is_exist_userId == None:
        return statusCode.no_exist_user
    elif update_data == None: # 업데이트 할 데이터가 없음 -> today날짜 오류 (로그인 아이디 일치여부는 위에 if문에서 먼저 잡아주기때문)
        return statusCode.not_equal_today
    elif login_id == None:
        return statusCode.not_id
    elif today == None:
        return statusCode.not_habit_today
    elif is_exist_userId and update_data:
        
        update_data.name = name
        update_data.today = today
        update_data.cName = cName
        db.add(update_data)
        db.commit()
        return statusCode.success
    else:
        return statusCode.unexpected_error

# 타임 리스트 삭제
@router.delete("/time_delete/{login_id}/{list_id}",status_code=200)
async def time_delete(login_id: str, list_id:int, db:Session = Depends(get_db)):
    """
    타임 삭제 API
    """
    exist_user_id = db.query(models.Users.id).filter_by(login_id = login_id).first()
    exist_time = db.query(models.TimeTracker).filter_by(user_id = exist_user_id.id, id=list_id).first()

    if exist_user_id == None:
        return statusCode.no_exist_user
    elif exist_user_id and exist_time: 
        db.query(models.TimeTracker).filter_by(user_id = exist_user_id.id, id=list_id).delete()
        db.commit()
        return statusCode.success
    elif None == exist_user_id: # login_id가 없는 경우
        return statusCode.not_id
    elif None == exist_time: # 해당 조건에 대한 habit_id가 없는 경우
        return statusCode.none_correction_data    
    else:
        return statusCode.unexpected_error
    


# @router.get("/play_click/{login_id}/{list_id}/{startTime}/{timeTaken}",status_code=200)
# async def play_click(login_id: str, list_id:int, startTime:str, timeTaken:str, db:Session = Depends(get_db)):
#     """
#     타임 리스트 시간 기록 시작 시 timetrackerorder 테이블에 정보 저장 API
#     """
#     exist_user_id = db.query(models.Users).filter_by(login_id = login_id).first()
#     exist_time = db.query(models.TimeTracker).filter_by(user_id = exist_user_id.id).first()
#     exist_time_order = db.query(models.TimeTrackerOrder).filter_by(user_id = exist_user_id.id, list_id = list_id).all()
    
#     if exist_user_id == None:
#         return statusCode.no_exist_user
#     elif login_id == None:
#         return statusCode.not_id
#     elif list_id == None:
#         return statusCode.no_list_id
#     elif exist_user_id.id == None:
#         return statusCode.not_id 
#     elif exist_time == None: # list_id 잘못넘겨주면 exist_time 존재하지 않음
#         return statusCode.no_exist_time_list
#     elif startTime == None:
#         return statusCode.no_time_startTime
#     elif exist_user_id and exist_time: 
#         if not exist_time_order: # 처음 생성 시
#             models.TimeTrackerOrder.create(db, auto_commit = True, user_id = exist_user_id.id, list_id=list_id, order = 1, startTime = startTime, endTime="None", timeTaken="00:00:00")
#             db.commit()
#             create_list = db.query(models.TimeTrackerOrder).filter_by(user_id = exist_user_id.id, list_id=list_id, order = maxOrder+1, startTime = startTime, endTime="None", timeTaken = "00:00:00").first()
#             create_result = {"create_list_id":create_list.list_id, "create_list_order":create_list.order, "create_list_startTime" : create_list.startTime, "create_list_endTime" : create_list.endTime, "create_list_timeTaken": create_list.timeTaken,"SUCCESS": 200}
#             return create_result
#         else: # 처음 이후  
#         # order 값이 제일 큰 애 찾기
#             maxIdx = 0
#             maxOrder = 1 # order 값 제일 큰 애 

#             for i in range(1, len(exist_time_order)): 
#                 if (exist_time_order[maxIdx].order <= exist_time_order[i].order):
#                     maxIdx = i 
#                 maxOrder = exist_time_order[maxIdx].order 
#             exist_time_test = db.query(models.TimeTrackerOrder.timeTaken).filter_by(user_id = exist_user_id.id, list_id = list_id, order = maxOrder - 1).all()
#             print(exist_time_test)
#             models.TimeTrackerOrder.create(db, auto_commit = True, user_id = exist_user_id.id, list_id = list_id, order = maxOrder+1, startTime = startTime, endTime="None", timeTaken = timeTaken)
#             db.commit() 

#             create_list = db.query(models.TimeTrackerOrder).filter_by(user_id = exist_user_id.id, list_id=list_id, order = maxOrder+1, startTime = startTime, endTime="None", timeTaken = timeTaken).first()
#             create_result = {"create_list_id":create_list.list_id, "create_list_order":create_list.order, "create_list_startTime" : create_list.startTime, "create_list_endTime" : create_list.endTime, "create_list_timeTaken": create_list.timeTaken,"SUCCESS": 200}
#             return create_result
#     else:
#         return statusCode.unexpected_error

# play 클릭 시 앱->서버 -타임 테이큰 디비 수정
@router.get("/play_click/{login_id}/{list_id}/{startTime}",status_code=200)
async def play_click(login_id: str, list_id:int, startTime:str, db:Session = Depends(get_db)):
    """
    타임 리스트 시간 기록 시작 시 timetrackerorder 테이블에 정보 저장 API
    """
    exist_user_id = db.query(models.Users).filter_by(login_id = login_id).first()
    exist_time = db.query(models.TimeTracker).filter_by(user_id = exist_user_id.id).first()
    exist_time_order = db.query(models.TimeTrackerOrder).filter_by(user_id = exist_user_id.id, list_id = list_id).all()
    result = "{"

    if exist_user_id == None:
        return statusCode.no_exist_user
    elif login_id == None:
        return statusCode.not_id
    elif list_id == None:
        return statusCode.no_list_id
    elif exist_time == None: # list_id 잘못넘겨주면 exist_time 존재하지 않음
        return statusCode.no_exist_time_list
    elif startTime == None:
        return statusCode.no_time_startTime
    elif exist_user_id and exist_time:
        if exist_time_order == None: # 처음 생성 시
            models.TimeTrackerOrder.create(db, auto_commit = True, user_id = exist_user_id.id, list_id=list_id, order = 0, startTime = startTime, endTime="None", timeTaken="00:00:00")
            db.commit()

            create_list = db.query(models.TimeTrackerOrder).filter_by(user_id = exist_user_id.id, list_id=list_id, order = 0, startTime = startTime, endTime="None", timeTaken="00:00:00").first()
            result += ("\"create_list_id" + "\":\"" + str(create_list.list_id) + "\", " 
                      +"\"create_list_order"+"\" : \""+ str(create_list.order) + "\", " 
                      +"\"create_list_startTime"+"\" : \""+ create_list.startTime +"\", "
                      +"\"create_list_endTime"+"\" : \""+ create_list.endTime +"\", "
                      +"\"create_list_timeTaken"+"\" : \""+ create_list.timeTaken +"\", "
                      + "\"SUCCESS"+"\" : \"" + str(200) + "\"" + "}")
            return json.loads(result)
        else: # 처음 이후  
            maxIdx = 0
            maxOrder = 0 # order 값 제일 큰 애
            for i in range(1, len(exist_time_order)):
                if (exist_time_order[maxIdx].order < exist_time_order[i].order):
                    maxIdx = i
                maxOrder = exist_time_order[maxIdx].order 
            models.TimeTrackerOrder.create(db, auto_commit = True, user_id = exist_user_id.id, list_id=list_id, order = maxOrder+1, startTime = startTime, endTime="None", timeTaken="00:00:00")
            db.commit()
            
            create_list = db.query(models.TimeTrackerOrder).filter_by(user_id = exist_user_id.id, list_id=list_id, order = maxOrder+1, startTime = startTime, endTime="None", timeTaken="00:00:00").first()
            result += ("\"create_list_id" + "\":\"" + str(create_list.list_id) + "\", " 
                      +"\"create_list_order" +"\" : \""+ str(create_list.order) + "\", " 
                      +"\"create_list_startTime"+"\" : \""+ create_list.startTime +"\", "
                      +"\"create_list_endTime"+"\" : \""+ create_list.endTime +"\", "
                      +"\"create_list_timeTaken"+"\" : \""+ create_list.timeTaken +"\", ")

            # total_timeTaken 구하는 코드!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # 타임 테이큰값이 '00:00:00'이 아닌 튜플 찾아서 타임 테이큰 총 합 구하기
            exist_timeTaken = db.query(models.TimeTrackerOrder).filter_by(user_id = exist_user_id.id, list_id=list_id).all()
            total_taken = "00:00:00" # 일단 타임 테이큰 "00:00:00"으로 놓고
            for i in range(len(exist_timeTaken)):
                if exist_timeTaken[i].timeTaken != "00:00:00":
                    total_taken = datetime.strptime(total_taken, "%H:%M:%S") # 시간 형식으로 바꿈
                    pre_taken = datetime.strptime(exist_timeTaken[i].timeTaken, "%H:%M:%S") # 튜플에 저장된 timeTaken값을 시간 형식으로 바꿈
                    total_taken += timedelta(hours=pre_taken.hour, minutes=pre_taken.minute, seconds=pre_taken.second) # 시간 형식으로 바꾼 두 값 더해
                    # 더한 결과 다시 스트링으로 변환
                    total_taken = str(total_taken).split(" ")[1] # 이 과정안해주면 반복문 돌 때 total_taken 형식이 datetime이라 오류남 + "1900-01-01 00:00:00"이 형식이라 시간만 사용하려고 split 씀
            # 반복문 다 돌고 나서
            total_taken = str(total_taken) # 시간형식 스트링으로 바꾸기
            if len(total_taken) < 8: 
                total_taken = "0" + str(total_taken) # 이건 "00:00:00" 형식으로 맞추기 위함
 
            result += "\"total_timeTaken" + "\":\"" + str(total_taken) + "\", " + "\"SUCCESS"+"\" : \"" + str(200) + "\"" + "}"
                    
            return json.loads(result)
    else:
        return statusCode.unexpected_error
    
@router.get("/pause_click/{login_id}/{list_id}/{endTime}",status_code=200)
async def pause_click(login_id: str, list_id:int, endTime:str, db:Session = Depends(get_db)):
    """
    pause 클릭 했을 때 사용 API
    """
    exist_user_id = db.query(models.Users.id).filter_by(login_id = login_id).first()
    exist_time = db.query(models.TimeTrackerOrder).filter_by(user_id = exist_user_id.id, list_id = list_id).all()

    if exist_user_id == None:
        return statusCode.no_exist_user
    elif login_id == None:
        return statusCode.not_id
    elif list_id == None:
        return statusCode.no_list_id
    elif exist_time == None: # list_id 잘못넘겨주면 exist_time 존재하지 않음
        return statusCode.no_exist_time_list
    elif exist_user_id and exist_time:   
        # order 값이 제일 큰 애 찾기
        maxIdx = 0
        maxOrder = 1 # order 값 제일 큰 애
        for i in range(1, len(exist_time)):
            if (exist_time[maxIdx].order < exist_time[i].order):
                maxIdx = i
            maxOrder = exist_time[maxIdx].order
        # timetaken 계산하기
        # (endTime - startTime) + order값이 동일한 튜플의 timetaken 집어넣기
        time_startTime = datetime.strptime(exist_time[maxIdx].startTime, "%H:%M:%S")
        time_endTime = datetime.strptime(endTime, "%H:%M:%S")
        timeTaken = str(time_endTime-time_startTime)
        if len(timeTaken) < 8:
            timeTaken = "0" + str(time_endTime-time_startTime)  

        if datetime.strptime(timeTaken, "%H:%M:%S") < datetime.strptime("00:01:00", "%H:%M:%S"):
            db.query(models.TimeTrackerOrder).filter_by(user_id = exist_user_id.id, list_id = list_id, order = exist_time[maxIdx].order).delete()
            db.commit()

            # total_timeTaken 구하는 코드!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # 타임 테이큰값이 '00:00:00'이 아닌 튜플 찾아서 타임 테이큰 총 합 구하기
            exist_timeTaken = db.query(models.TimeTrackerOrder).filter_by(user_id = exist_user_id.id, list_id=list_id).all()
            total_taken = "00:00:00" # 일단 타임 테이큰 "00:00:00"으로 놓고
            for i in range(len(exist_timeTaken)):
                if exist_timeTaken[i].timeTaken != "00:00:00":
                    total_taken = datetime.strptime(total_taken, "%H:%M:%S") # 시간 형식으로 바꿈
                    pre_taken = datetime.strptime(exist_timeTaken[i].timeTaken, "%H:%M:%S") # 튜플에 저장된 timeTaken값을 시간 형식으로 바꿈
                    total_taken += timedelta(hours=pre_taken.hour, minutes=pre_taken.minute, seconds=pre_taken.second) # 시간 형식으로 바꾼 두 값 더해
                    # 더한 결과 다시 스트링으로 변환
                    total_taken = str(total_taken).split(" ")[1] # 이 과정안해주면 반복문 돌 때 total_taken 형식이 datetime이라 오류남 + "1900-01-01 00:00:00"이 형식이라 시간만 사용하려고 split 씀
            # 반복문 다 돌고 나서
            total_taken = str(total_taken) # 시간형식 스트링으로 바꾸기
            if len(total_taken) < 8: 
                total_taken = "0" + str(total_taken) # 이건 "00:00:00" 형식으로 맞추기 위함

            return {"total_timeTaken":total_taken, "tuple":"None", "SUCCESS":200}
        else:
            models.TimeTrackerOrder.create(db, auto_commit = True, user_id = exist_user_id.id, list_id=list_id, order=maxOrder, startTime=exist_time[maxIdx].startTime, endTime=endTime, timeTaken=timeTaken)
            db.commit()

            create_list = db.query(models.TimeTrackerOrder).filter_by(user_id = exist_user_id.id, list_id=list_id, order=maxOrder, startTime=exist_time[maxIdx].startTime, endTime=endTime, timeTaken=timeTaken).first()
            result = "{"
            result += ("\"create_list_id"+ "\":\"" + str(create_list.list_id) + "\", " 
                      +"\"create_list_order"+"\" : \""+ str(create_list.order) + "\", " 
                      +"\"create_list_startTime"+"\" : \""+ create_list.startTime +"\", "
                      +"\"create_list_endTime"+"\" : \""+ create_list.endTime +"\", "
                      +"\"create_list_timeTaken"+"\" : \""+ create_list.timeTaken +"\", ")
            
            # total_timeTaken 구하는 코드!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # 타임 테이큰값이 '00:00:00'이 아닌 튜플 찾아서 타임 테이큰 총 합 구하기
            exist_timeTaken = db.query(models.TimeTrackerOrder).filter_by(user_id = exist_user_id.id, list_id=list_id).all()
            total_taken = "00:00:00" # 일단 타임 테이큰 "00:00:00"으로 놓고
            for i in range(len(exist_timeTaken)):
                if exist_timeTaken[i].timeTaken != "00:00:00":
                    total_taken = datetime.strptime(total_taken, "%H:%M:%S") # 시간 형식으로 바꿈
                    pre_taken = datetime.strptime(exist_timeTaken[i].timeTaken, "%H:%M:%S") # 튜플에 저장된 timeTaken값을 시간 형식으로 바꿈
                    total_taken += timedelta(hours=pre_taken.hour, minutes=pre_taken.minute, seconds=pre_taken.second) # 시간 형식으로 바꾼 두 값 더해
                    # 더한 결과 다시 스트링으로 변환
                    total_taken = str(total_taken).split(" ")[1] # 이 과정안해주면 반복문 돌 때 total_taken 형식이 datetime이라 오류남 + "1900-01-01 00:00:00"이 형식이라 시간만 사용하려고 split 씀
            # 반복문 다 돌고 나서
            total_taken = str(total_taken) # 시간형식 스트링으로 바꾸기
            if len(total_taken) < 8: 
                total_taken = "0" + str(total_taken) # 이건 "00:00:00" 형식으로 맞추기 위함

            result += "\"total_timeTaken" + "\":\"" + str(total_taken) + "\", " + "\"SUCCESS"+"\" : \"" + str(200) + "\"" + "}"
                    
            return json.loads(result)
    else:
        return statusCode.unexpected_error

# timeTrackerOrder 정보 반환하는 메소드
@router.get("/get_timer_info/{login_id}/{list_id}",status_code=200)
async def get_time_list(login_id: str, list_id:int, db:Session = Depends(get_db)):
    """
    TimeTrackerOrder 정보 확인 API 
    """
    is_exist_userId = db.query(models.Users.id).filter_by(login_id=login_id).first()
    is_exist_timeOrder = db.query(models.TimeTrackerOrder).filter_by(user_id = is_exist_userId.id, list_id = list_id).all()
    is_exist_Torder = db.query(models.TimeTrackerOrder.order).filter_by(user_id = is_exist_userId.id, list_id = list_id).first() #timetrackerOrder.order 값이 없을 때 경우의

    result_timeOrder_list = "{"
    
    if is_exist_userId == None:
        return statusCode.no_exist_user
    elif login_id == None: 
        return statusCode.not_id
    elif list_id == None:
        return statusCode.no_list_id
    elif is_exist_timeOrder == None:
        return statusCode.no_exist_time_list
    elif is_exist_Torder == None:
        result = {"timeOrder_total":0}
        return result
    elif login_id and list_id and is_exist_timeOrder:
        result_timeOrder_list += "\"timeOrder_total"+"\" : \""+ str(len(is_exist_timeOrder)) + "\", "
        for i in range(0,len(is_exist_timeOrder)):
            if i == len(is_exist_timeOrder)-1: # 마지막 줄이면 끝에 , 뺌
                result_timeOrder_list += ("\"timeOrder_order"+str(i) + "\":\"" + str(is_exist_timeOrder[i].order) + "\", " 
                                    + "\"timeOrder_startTime"+str(i)+"\" : \""+ is_exist_timeOrder[i].startTime + "\", " 
                                    + "\"timeOrder_endTime"+str(i)+"\" : \"" + is_exist_timeOrder[i].endTime +"\", " 
                                    +"\"timeOrder_timeTaken"+str(i)+"\" : \""+ is_exist_timeOrder[i].timeTaken +"\", "
                                    + "\"SUCCESS"+"\" : \"" + str(200) + "\"")
            else: # 마지막 줄이 아니면 , 추가
                result_timeOrder_list += ("\"timeOrder_order"+str(i) + "\":\"" + str(is_exist_timeOrder[i].order) + "\", " 
                                    + "\"timeOrder_startTime"+str(i)+"\" : \""+ is_exist_timeOrder[i].startTime + "\", " 
                                    +"\"timeOrder_endTime"+str(i)+"\" : \""+ is_exist_timeOrder[i].endTime +"\", "
                                    +"\"timeOrder_timeTaken"+str(i)+"\" : \""+ is_exist_timeOrder[i].timeTaken +"\", ")
        result_timeOrder_list += "}"
        return json.loads(result_timeOrder_list)
    else:
        return statusCode.unexpected_error

# 10분 단위로 잘라서 보내주기
@router.get("/get_round_time/{login_id}/{list_id}",status_code=200)
async def get_round_time(login_id: str, list_id:int, db:Session = Depends(get_db)):
    """
    TimeTrackerOrder 정보 확인 API
    """
    is_exist_userId = db.query(models.Users.id).filter_by(login_id=login_id).first()
    is_exist_timeOrder = db.query(models.TimeTrackerOrder).filter_by(user_id = is_exist_userId.id, list_id = list_id).all()
    result_timeOrder_list = "{"
    
    if is_exist_userId == None:
        return statusCode.no_exist_user
    elif login_id == None:
        return statusCode.not_id
    elif list_id == None:
        return statusCode.no_list_id
    elif is_exist_timeOrder == None:
        return statusCode.no_exist_time_list
    elif login_id and is_exist_timeOrder:
        # 보내줄 튜플 수 찾기
        total = 0
        for i in range(len(is_exist_timeOrder)):
            #조건 추가, 반올림
            if is_exist_timeOrder[i].endTime != "None":
                total += 1               
                time_startTime = datetime.strptime(is_exist_timeOrder[i].startTime, "%H:%M:%S")
                time_endTime = datetime.strptime(is_exist_timeOrder[i].endTime, "%H:%M:%S")
    
                timeTaken = str(time_endTime-time_startTime)

                # 형식 처리 먼저
                if len(timeTaken) < 8: # 분/초 만 기록되었을 때도 확인하고 처리해주기
                    timeTaken = "0" + str(time_endTime-time_startTime)

                # timeTaken --> "hh:mm:ss"
                # 3번째 인덱스부터 문자 2개 잘라서(mm) 그걸 int로 바꾸고 
                # round 처리했을 때 값이 60을 넘으면 00으로 바꾸고 
                # 시간+1
                # 그러고 다시 다 합쳐서 하나의 문자열로 만들기
                hour = timeTaken.split(':')[0] 
                min = timeTaken.split(':')[1] 

                if round(int(min), -1) >= 60:
                    min = "00"
                    hour += 1
                else:
                    min = round(int(min), -1)
                timeTaken = hour + ":" + str(min) + ":" + "00"   

                result_timeOrder_list += ("\"timeOrder_list_id"+str(i) + "\":\"" + str(is_exist_timeOrder[i].list_id) + "\", " 
                                    + "\"timeOrder_startTime"+str(i)+"\" : \""+ is_exist_timeOrder[i].startTime + "\", " 
                                    +"\"timeOrder_endTime"+str(i)+"\" : \""+ is_exist_timeOrder[i].endTime +"\", "
                                    +"\"timeOrder_timeTaken"+str(i)+"\" : \""+ timeTaken +"\", ")

        result_timeOrder_list += "\"timeOrder_tosal"+"\" : \""+ str(total) + "\", " + "\"SUCCESS"+"\" : \"" + str(200) + "\"" + "}"
        return json.loads(result_timeOrder_list)
    else:
        return statusCode.unexpected_error

    # 예) timeTaken이 04:52:23일 때 --> 04:50:00으로 변환해서 보내주기
    # 반환해야할 값: list_id, startTime, endTime, timeTaken_round_10