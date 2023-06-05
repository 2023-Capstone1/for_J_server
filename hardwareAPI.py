from fastapi import APIRouter, FastAPI, HTTPException
from requests import Session
from fastapi.params import Depends
from db import get_db

import models, datetime, random, statusCode
import json

router = APIRouter(prefix="/hardwareAPI",tags=["hardwareAPI"])

# 하루 동안의 투두 진행도 확인 테스트
@router.get("/progress/{login_id}/{date}",status_code=200)
async def user_info(login_id:str, date:str, db:Session = Depends(get_db)):
    """
    현재 진행도 확인 API
    """
    is_exist_user_info = db.query(models.Users).filter_by(login_id=login_id).first()
    is_exist_todo_in_date = db.query(models.Todo).filter_by(user_id=is_exist_user_info.id, date = date).all()
    
    if is_exist_user_info == None:
        return statusCode.not_id
    elif is_exist_user_info and is_exist_todo_in_date:
        todo_complete = 0
        for i in range(len(is_exist_todo_in_date)):
            if is_exist_todo_in_date[i].state == 1:
                todo_complete += 1
        
        if not todo_complete:
            result = 0
        else: 
            result = round((todo_complete / len(is_exist_todo_in_date)) * 100)

        return result
    else:
        return statusCode.unexpected_error 