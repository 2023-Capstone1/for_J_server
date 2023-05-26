from fastapi import APIRouter, FastAPI, HTTPException
from requests import Session
from fastapi.params import Depends
from sqlalchemy import desc
from db import get_db
from pydantic import BaseModel
from email_validator import validate_email, EmailNotValidError
from token_utils import create_email_verification_token, verify_email_verification_token
from email_utils import send_email_verification_email

import models, datetime, random, statusCode
import json

router = APIRouter(prefix="/todoAPI",tags=["todoAPI"])
    
# 투두 최초 저장 메소드
@router.post("/set_todo/{login_id}/{name}/{date}/{cName}/{state}",status_code=200)
async def set_todo(login_id: str, name: str, date:str, cName:str, state:int, db:Session = Depends(get_db)):
    """
    투두 리스트 생성 API
    """
    is_exist_userId = db.query(models.Users.id).filter_by(login_id=login_id).first()

    if is_exist_userId == None:
        return statusCode.no_exist_user
    elif login_id == None:
        return statusCode.not_id
    elif date == None:
        return statusCode.not_todo_date
    elif cName == None:
        return statusCode.not_todo_cName
    elif state == None:
        return statusCode.not_todo_state
    elif is_exist_userId:
        models.Todo.create(db, auto_commit = True, user_id = is_exist_userId.id, name = name, date = date, cName = cName, state = state)
        return statusCode.success
    else:
        return statusCode.unexpected_error
    
@router.put("/update_todo/{login_id}/{list_id}/{name}/{date}/{cName}/{state}",status_code=200)
async def update_todo(login_id: str, list_id:int, name: str, date:str, cName:str, state:int, db:Session = Depends(get_db)):
    """
    투두 리스트 수정 API
    """
    is_exist_userId = db.query(models.Users.id).filter_by(login_id=login_id).first()

    update_data = db.query(models.Todo).filter_by(user_id = is_exist_userId.id, id=list_id).first()
    
    if is_exist_userId == None:
        return statusCode.no_exist_user
    elif update_data == None:
        return statusCode.unexpected_error
    elif login_id == None:
        return statusCode.not_id
    elif date == None:
        return statusCode.not_todo_date
    elif cName == None:
        return statusCode.not_todo_cName
    elif state == None:
        return statusCode.not_todo_state
    elif is_exist_userId:
        if update_data:
            update_data.name = name
            update_data.date = date
            update_data.cName = cName
            update_data.state = state
            db.add(update_data)
            db.commit()
        return statusCode.success
    else:
        return statusCode.unexpected_error

# 수진이 파트 todo 튜플 하나만 가져오는 메소드
@router.get("/get_todo_to_update/{login_id}/{list_id}/{name}/{date}",status_code=200)
async def get_todo_to_update(login_id: str, list_id:int, name: str, date:str, db:Session = Depends(get_db)):
    """
    투두 리스트 값 한 개 확인 API
    """
    is_exist_userId = db.query(models.Users.id).filter_by(login_id=login_id).first()
    todo_list = db.query(models.Todo).filter_by(user_id = is_exist_userId.id, name=name, date= date, id=list_id).first()

    result_todo_list = {"todo_list_id":todo_list.id, "todo_name":todo_list.name, "todo_date" : todo_list.date, "todo_cName" : todo_list.cName, "todo_state": todo_list.state, "SUCCESS": 200}

    if is_exist_userId == None:
        return statusCode.no_exist_user
    elif login_id == None:
        return statusCode.not_id
    elif date == None:
        return statusCode.not_todo_date
    elif todo_list == None:
        return statusCode.no_exist_todo_list
    elif login_id and name and date:
        return result_todo_list
    else:
        return statusCode.unexpected_error

# 다솔이 파트 get_todo_list 날짜 클릭했을 때 해당 날짜의 모든 리스트 튜플 가져와야 되는 메소드 
@router.get("/get_todo_list/{login_id}/{date}",status_code=200)
async def get_todo_list(login_id: str, date:str, db:Session = Depends(get_db)):
    """
    특정 날짜의 모든 투두 리스트 값 확인 API
    """
    is_exist_userId = db.query(models.Users.id).filter_by(login_id=login_id).first()
    is_exist_todo = db.query(models.Todo).filter_by(user_id = is_exist_userId.id, date = date).all()

    result_todo_list = "{"
    
    if is_exist_userId == None:
        return statusCode.no_exist_user
    elif login_id == None:
        return statusCode.not_id
    elif date == None:
        return statusCode.not_todo_date
    elif is_exist_todo == None:
        return statusCode.no_exist_todo_list
    elif login_id and date and is_exist_todo:
        result_todo_list += "\"todo_total"+"\" : \""+ str(len(is_exist_todo)) + "\", "
        for i in range(0,len(is_exist_todo)):
            if i == len(is_exist_todo)-1: # 마지막 줄이면 끝에 , 뺌
                result_todo_list += "\"todo_list_id"+str(i) + "\":\"" + str(is_exist_todo[i].id) + "\", " + "\"todo_name"+str(i)+"\" : \""+ is_exist_todo[i].name + "\", " +"\"todo_cName"+str(i)+"\" : \"" + is_exist_todo[i].cName +"\", " + "\"todo_state"+str(i) + "\" : \"" + str(is_exist_todo[i].state)+"\", " + "\"SUCCESS"+"\" : \"" + str(200) + "\""
            else: # 마지막 줄이 아니면 , 추가
                result_todo_list += "\"todo_list_id"+str(i) + "\":\"" + str(is_exist_todo[i].id) + "\", " + "\"todo_name"+str(i)+"\" : \""+ is_exist_todo[i].name + "\", " +"\"todo_cName"+str(i)+"\" : \""+ is_exist_todo[i].cName +"\", "+ "\"todo_state"+str(i)+"\" : \""+ str(is_exist_todo[i].state)+"\", "
        result_todo_list += "}"
        return json.loads(result_todo_list)
    else:
        return statusCode.unexpected_error

# 특정 날짜에 사용되는 카테고리 모두 반환
@router.get("/get_todo_date_category/{login_id}/{date}",status_code=200)
async def get_todo_date_category(login_id: str, date:str, db:Session = Depends(get_db)):
    """
    특정 날짜에서 사용되는 모든 투두 카테고리 값 확인 API
    """
    is_exist_userId = db.query(models.Users.id).filter_by(login_id=login_id).first()
    is_exist_todo = db.query(models.Todo).filter_by(user_id = is_exist_userId.id, date= date).all()    

    result_todo_list = "{"
    
    if is_exist_userId == None:
        return statusCode.no_exist_user
    elif login_id == None:
        return statusCode.not_id
    elif date == None:
        return statusCode.not_todo_date  #디비에 없는 날짜 오류 추가하기
    elif is_exist_todo == None:
        return statusCode.no_exist_todo_list
    elif login_id and date and is_exist_todo:
        result_todo_list += "\"todo_category_total"+"\" : \""+ str(len(is_exist_todo)) + "\", "
        for i in range(0,len(is_exist_todo)):
            is_exist_category_color = db.query(models.Category).filter_by(user_id = is_exist_userId.id, name = is_exist_todo[i].cName).first() # 투두 카테고리 색상도 같이 보내주기 위함
            print(is_exist_category_color)
            if i == len(is_exist_todo)-1: # 마지막 줄이면 끝에 , 뺌
                result_todo_list += "\"todo_cName"+str(i)+"\" : \""+ is_exist_todo[i].cName + "\", " + "\"todo_cColor"+str(i)+"\" : \""+ is_exist_category_color.color + "\", " + "\"SUCCESS"+"\" : \"" + str(200) + "\""
            else: # 마지막 줄이 아니면 , 추가
                result_todo_list += "\"todo_cName"+str(i)+"\" : \""+ is_exist_todo[i].cName + "\", " + "\"todo_cColor"+str(i)+"\" : \""+ is_exist_category_color.color + "\", "
        result_todo_list += "}"
        print(result_todo_list)
        return json.loads(result_todo_list)
    else:
        return statusCode.unexpected_error

@router.get("/get_todo_list_state/{login_id}/{list_id}/{name}/{date}",status_code=200)
async def get_todo_list_state(login_id: str, list_id:int, name: str, date: str, db:Session = Depends(get_db)):
    """"
    투두 리스트의 상태 가져오기 API
    """
    is_exist_userId = db.query(models.Users.id).filter_by(login_id = login_id).first()
    todo_list = db.query(models.Todo).filter_by(user_id = is_exist_userId.id, name=name, date=date, id=list_id).first()

    result_todo_list = {"todo_state": todo_list.state, "SUCCESS": 200}

    if is_exist_userId == None:
        return statusCode.no_exist_user
    elif todo_list.name == name and todo_list.date == date: # 리스트 이름이랑 리스트의 날짜가 모두 같을 때
        return result_todo_list # 값 리턴
    elif is_exist_userId == None:
        return statusCode.not_id
    elif todo_list == None:
        return statusCode.no_exist_todo_list
    elif todo_list.name == None: 
        return statusCode.not_todo_name
    elif todo_list.date == None: 
        return statusCode.not_todo_date
    else :
        return statusCode.unexpected_error

@router.put("/update_todo_list_state/{login_id}/{list_id}/{name}/{date}/{state}",status_code=200)
async def update_todo_list_state(login_id: str, list_id:int, name: str, date:str, state:int, db:Session = Depends(get_db)):
    """
    투두 리스트의 상태 수정 API
    """
    is_exist_userId = db.query(models.Users).filter_by(login_id=login_id).first() 
    update_state = db.query(models.Todo).filter_by(user_id = is_exist_userId.id, name = name, date = date, id=list_id).first() 

    if is_exist_userId == None:
        return statusCode.no_exist_user
    elif update_state == None:
        return statusCode.no_exist_todo_list
    elif list_id == None:
        return statusCode.no_list_id
    elif name == None:
        return statusCode.not_todo_name
    elif date == None:
        return statusCode.not_todo_date
    elif state == None:
        return statusCode.not_todo_state
    elif is_exist_userId and update_state:
        update_state.state = state
        db.add(update_state)
        db.commit()
        return statusCode.success
    else:
        return statusCode.unexpected_error

@router.delete("/todo_delete/{login_id}/{list_id}",status_code=200)
async def todo_delete(login_id: str, list_id:int, db:Session = Depends(get_db)):
    """
    투두 삭제 API
    """
    exist_user_id = db.query(models.Users.id).filter_by(login_id = login_id).first()
    exist_todo = db.query(models.Todo).filter_by(user_id = exist_user_id.id, id=list_id).first()

    if exist_user_id == None:
        return statusCode.no_exist_user
    elif exist_user_id and exist_todo: 
        db.query(models.Todo).filter_by(user_id = exist_user_id.id, id=list_id).delete()
        db.commit()
        return statusCode.success
    elif None == exist_user_id: # login_id가 없는 경우
        return statusCode.not_id
    elif None == exist_todo: # 해당 조건에 대한 habit_id가 없는 경우
        return statusCode.none_correction_data    
    else:
        return statusCode.unexpected_error
    
@router.get("/get_todo_list_plus_color/{login_id}/{date}",status_code=200)
async def get_todo_list_plus_color(login_id: str, date: str, db:Session = Depends(get_db)):
    """
    특정 날짜의 모든 투두 리스트 값 + 카테고리 컬러까지 확인 API
    """
    is_exist_userId = db.query(models.Users).filter_by(login_id=login_id).first()
    is_exist_todo = db.query(models.Todo).filter_by(user_id = is_exist_userId.id, date = date).all()

    result_todo_list = "{"
    
    if is_exist_userId == None:
        return statusCode.no_exist_user 
    elif login_id == None:
        return statusCode.not_id
    elif date == None:
        return statusCode.not_todo_date
    elif is_exist_todo == None: 
        return statusCode.no_exist_todo_list
    elif login_id and date and is_exist_todo:
        result_todo_list += "\"todo_total"+"\" : \""+ str(len(is_exist_todo)) + "\", "
        for i in range(0,len(is_exist_todo)):
            is_exist_category_color = db.query(models.Category).filter_by(user_id = is_exist_userId.id, name = is_exist_todo[i].cName).first() # 투두 카테고리 색상도 같이 보내주기 위함
            if i == len(is_exist_todo)-1: # 마지막 줄이면 끝에 , 뺌
                result_todo_list += ("\"todo_list_id"+str(i) + "\":\"" + str(is_exist_todo[i].id) + "\", " + "\"todo_name"+str(i)+"\" : \""+ is_exist_todo[i].name + "\", " 
                                    +"\"todo_cName"+str(i)+"\" : \""+ is_exist_todo[i].cName +"\", "+"\"todo_cColor"+str(i)+"\" : \"" + is_exist_category_color.color +"\", "
                                    + "\"todo_state"+str(i) + "\" : \"" + str(is_exist_todo[i].state)+"\", " + "\"SUCCESS"+"\" : \"" + str(200) + "\"")
            else: # 마지막 줄이 아니면 , 추가
                result_todo_list += ("\"todo_list_id"+str(i) + "\":\"" + str(is_exist_todo[i].id) + "\", " + "\"todo_name"+str(i)+"\" : \""+ is_exist_todo[i].name + "\", " 
                                    +"\"todo_cName"+str(i)+"\" : \""+ is_exist_todo[i].cName +"\", "+"\"todo_cColor"+str(i)+"\" : \"" + is_exist_category_color.color +"\", "
                                    + "\"todo_name"+str(i)+"\" : \""+ is_exist_todo[i].name + "\", " + "\"todo_state"+str(i)+"\" : \""+ str(is_exist_todo[i].state)+"\", ")
        result_todo_list += "}"
        return json.loads(result_todo_list)
    else:
        return statusCode.unexpected_error
