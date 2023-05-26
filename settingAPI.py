from fastapi import APIRouter, FastAPI, HTTPException
from requests import Session
from fastapi.params import Depends
from db import get_db

import models, statusCode

router = APIRouter(prefix="/settingAPI",tags=["settingAPI"])

@router.get("/get_setting_info/{login_id}",status_code=200)
async def get_setting_info(login_id: str, db:Session = Depends(get_db)):
    """
    setting 값 불러오는 API
    """
    is_exist_userId = db.query(models.Users.id).filter_by(login_id=login_id).first()
    is_exist_setting = db.query(models.Setting).filter_by(user_id=is_exist_userId.id).first()
    
    if is_exist_userId == None:
        return statusCode.no_exist_user
    elif login_id == None:
        return statusCode.not_id
    elif is_exist_userId:
        result = {"alarm_switch": is_exist_setting.alarm_switch, "todo_time":is_exist_setting.todo_time, "todo_switch":is_exist_setting.todo_switch, 
                  "habit_time":is_exist_setting.habit_time,"habit_switch":is_exist_setting.habit_switch,
                  "calendar_time":is_exist_setting.calendar_time,"calendar_switch":is_exist_setting.calendar_switch, 
                  "time_switch":is_exist_setting.time_switch, 
                  "dark_mode":is_exist_setting.dark_mode,"SUCCESS": 200}
        return result
    else:
        return statusCode.unexpected_error
    
@router.put("/setting_info_update/{login_id}/{alarm_switch}/{todo_time}/{todo_switch}/{habit_time}/{habit_switch}/{calendar_time}/{calendar_switch}/{time_switch}",status_code=200)
async def pw_update(login_id:str, alarm_switch:int, todo_time:str, todo_switch:int, habit_time:str, habit_switch:int, calendar_time:str, calendar_switch:int, time_switch:int, db:Session = Depends(get_db)):
    """
    setting 값 수정 API
    """
    get_id = db.query(models.Users).filter_by(login_id=login_id).first()
    update_data = db.query(models.Setting).filter_by(user_id = get_id.id).first()

    if get_id:
        update_data.alarm_switch = alarm_switch
        update_data.todo_time = todo_time
        update_data.todo_switch = todo_switch
        update_data.habit_time = habit_time
        update_data.habit_switch = habit_switch
        update_data.calendar_time = calendar_time
        update_data.calendar_switch = calendar_switch
        update_data.time_switch = time_switch
        db.add(update_data)
        db.commit()
        return statusCode.success
    elif None == get_id:
        return statusCode.not_id
    
    return statusCode.unexpected_error
    
# 전체 일정 삭제 (Calendar, Todo, Habit, TimeTracker 테이블 날리기)
@router.delete("/delete_all_schedule/{login_id}",status_code=200)
async def delete_all_schedule(login_id: str, db:Session = Depends(get_db)):
    """
    전체 일정 삭제 API
    """
    exist_user_id = db.query(models.Users).filter_by(login_id = login_id).first()

    if exist_user_id:
        # db.query(models.Calendar).filter(models.Calendar.user_id == login_id).delete()
        db.query(models.Todo).filter(models.Todo.user_id == exist_user_id.id).delete()
        db.query(models.Habit).filter(models.Habit.user_id == exist_user_id.id).delete()
        db.query(models.TimeTracker).filter(models.TimeTracker.user_id == exist_user_id.id).delete()
        db.query(models.TimeTrackerOrder).filter(models.TimeTrackerOrder.user_id == exist_user_id.id).delete()
        db.commit()
        return statusCode.success
    elif exist_user_id == None:
        return statusCode.not_id
    else:
        return statusCode.unexpected_error
    
@router.delete("/delete_all_todo/{login_id}",status_code=200)
async def delete_all_todo(login_id: str, db:Session = Depends(get_db)):
    """
    Todo 일정 삭제 API
    """
    exist_user_id = db.query(models.Users).filter_by(login_id = login_id).first()

    if exist_user_id:
        db.query(models.Todo).filter(models.Todo.user_id == exist_user_id.id).delete()
        db.commit()
        return statusCode.success
    elif exist_user_id == None:
        return statusCode.not_id
    else:
        return statusCode.unexpected_error
        
@router.delete("/delete_all_habit/{login_id}",status_code=200)
async def delete_all_habit(login_id: str, db:Session = Depends(get_db)):
    """
    Habit 일정 삭제 API
    """
    exist_user_id = db.query(models.Users).filter_by(login_id = login_id).first()

    if exist_user_id:
        db.query(models.Habit).filter(models.Habit.user_id == exist_user_id.id).delete()
        db.commit()
        return statusCode.success
    elif exist_user_id == None:
        return statusCode.not_id
    else:
        return statusCode.unexpected_error
    
@router.delete("/delete_all_calendar/{login_id}",status_code=200)
async def delete_all_calendar(login_id: str, db:Session = Depends(get_db)):
    """
    calenbar 일정 삭제 API
    """
    exist_user_id = db.query(models.Users).filter_by(login_id = login_id).first()

    if exist_user_id:
        db.query(models.Calendar).filter(models.Calendar.user_id == exist_user_id.id).delete()
        db.commit()
        return statusCode.success
    elif exist_user_id == None:
        return statusCode.not_id
    else:
        return statusCode.unexpected_error
    
@router.delete("/delete_all_timeTracker/{login_id}",status_code=200)
async def delete_all_timeTracker(login_id: str, db:Session = Depends(get_db)):
    """
    timeTracker 일정 삭제 API
    """
    exist_user_id = db.query(models.Users).filter_by(login_id = login_id).first()

    if exist_user_id:
        db.query(models.TimeTracker).filter(models.TimeTracker.user_id == exist_user_id.id).delete()
        db.query(models.TimeTrackerOrder).filter(models.TimeTrackerOrder.user_id == exist_user_id.id).delete()
        db.commit()
        return statusCode.success
    elif exist_user_id == None: 
        return statusCode.not_id
    else:
        return statusCode.unexpected_error