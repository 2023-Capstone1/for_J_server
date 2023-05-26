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

router = APIRouter(prefix="/categoryAPI",tags=["categoryAPI"])

@router.post("/set_todo_category/{login_id}/{name}/{color}/{isTodo}",status_code=200)
async def set_todo_category(login_id: str, name: str, color:str, isTodo: int, db:Session = Depends(get_db)):
    """
    todo_category 저장 API
    """
    is_exist_userId = db.query(models.Users.id).filter_by(login_id=login_id).first()
    
    if is_exist_userId == None:
        return statusCode.no_exist_user
    elif login_id == None:
        return statusCode.not_id
    # 자바에서 name, color 값 없이 메소드 호출 했을 때 404에러 발생
    elif name == None and color == None:
        return statusCode.no_category_name_color
    elif name == None:
        return statusCode.no_category_name
    elif color == None:
        return statusCode.no_category_color
    elif isTodo == None:
        return statusCode.no_isTodo
    elif is_exist_userId:
        models.Category.create(db, auto_commit = True, user_id = is_exist_userId.id, name = name, color = color, isTodo = isTodo)
        return statusCode.success
    else:
        return statusCode.unexpected_error
    
    
# 투두의 모든 카테고리 반환
@router.get("/get_todo_category_all/{login_id}/{isTodo}",status_code=200)
async def get_todo_category_all(login_id: str, isTodo: int, db:Session = Depends(get_db)):
    """
    todo_category 값 확인 API
    """
    is_exist_userId = db.query(models.Users.id).filter_by(login_id = login_id).first()
    todo_category = db.query(models.Category).filter_by(user_id = is_exist_userId.id, isTodo = 1).all()
    is_exist_user_loginId = db.query(models.Category.user_id).filter_by(user_id = is_exist_userId.id).first()
    result_todo_category = "{"

    if is_exist_userId == None:
        return statusCode.no_exist_user
    elif todo_category == None:
        return statusCode.no_todo_category
    elif is_exist_user_loginId == None:
        return statusCode.not_id
    elif login_id == None:
        return statusCode.not_id
    elif isTodo == None:
        return statusCode.no_isTodo
    elif todo_category == None:
        return statusCode.no_todo_category
    elif is_exist_userId and todo_category:
        result_todo_category += "\"todo_category_total"+"\" : \""+ str(len(todo_category)) + "\", "
        for i in range(0,len(todo_category)):
            # result_todo_category += "\"투두 카테고리 번호"+"\" : \""+ str(i+1) + "\", "
            if i == len(todo_category)-1: # 마지막 줄이면 끝에 , 뺌
                result_todo_category += "\"category_name"+str(i)+"\" : \""+ todo_category[i].name + "\", " +"\"category_color"+str(i)+"\" : \""+ todo_category[i].color +"\", " +"\"SUCCESS"+"\" : \""+ str(200) +"\""
            else: # 마지막 줄이 아니면 , 추가
                result_todo_category += "\"category_name"+str(i)+"\" : \""+ todo_category[i].name + "\", " +"\"category_color"+str(i)+"\" : \""+ todo_category[i].color +"\", "
        result_todo_category += "}"
        return json.loads(result_todo_category)
    else:
        return statusCode.unexpected_error

# 투두 카테고리 수정을 위해 카테고리 색상 가져오는 메소드
@router.get("/get_todo_category/{login_id}/{cName}/{isTodo}",status_code=200)
async def get_todo_category(login_id: str, cName: str, isTodo: int, db:Session = Depends(get_db)):
    """
    투두 리스트 수정 화면에서 카테고리 수정하는 API
    """
    is_exist_userId = db.query(models.Users.id).filter_by(login_id=login_id).first()
    todo_category_color = db.query(models.Category).filter_by(user_id = is_exist_userId.id, name=cName, isTodo=isTodo).first()

    if is_exist_userId == None:
        return statusCode.no_exist_user
    elif login_id == None:
        return statusCode.not_id
    elif cName == None:
        return statusCode.no_category_name
    elif isTodo == 0:
        return statusCode.isTodo_error
    elif todo_category_color == None:
        return statusCode.no_category_color
    elif login_id and todo_category_color:
        result = {"todo_category_color":todo_category_color.color, "SUCCESS": 200}
        return result
    else:
        return statusCode.unexpected_error
    
# 타임 카테고리 저장 (isTodo는 자바에서 0으로 보내줌)
@router.post("/set_time_category/{login_id}/{name}/{color}/{isTodo}",status_code=200)
async def set_time_category(login_id: str, name: str, color:str, isTodo: int, db:Session = Depends(get_db)):
    """
    time_category 저장 API
    """
    is_exist_userId = db.query(models.Users.id).filter_by(login_id=login_id).first()

    if is_exist_userId == None:
        return statusCode.no_exist_user
    elif login_id == None:
        return statusCode.not_id
    elif name == None:
        return statusCode.no_category_name
    elif color == None:
        return statusCode.no_category_color
    elif isTodo == None:
        return statusCode.no_isTodo
    elif is_exist_userId:
        models.Category.create(db, auto_commit = True, user_id = is_exist_userId.id, name = name, color = color, isTodo = isTodo)
        return statusCode.success
    else:
        return statusCode.unexpected_error

# 타임 카테고리 불러오기
# 저장한 타임 카테고리를 타임 추가 화면 안 카테고리 추가 다이얼로그에 보여주기 위함
@router.get("/get_time_category_all/{login_id}/{isTodo}",status_code=200)
async def get_time_category_all(login_id: str, isTodo: int, db:Session = Depends(get_db)):
    """
    time_category 값 확인 API
    """
    is_exist_userId = db.query(models.Users.id).filter_by(login_id=login_id).first()
    time_category = db.query(models.Category).filter_by(user_id = is_exist_userId.id, isTodo = 0).all()
    is_exist_user_loginId = db.query(models.Category.user_id).filter_by(user_id = is_exist_userId.id).first()
    result_time_category = "{"

    if is_exist_userId == None:
        return statusCode.no_exist_user
    elif time_category == None:
        return statusCode.no_time_category
    elif is_exist_user_loginId == None:
        return statusCode.not_equal_id
    elif login_id == None:
        return statusCode.not_id
    elif isTodo == None:
        return statusCode.no_isTodo
    elif is_exist_userId and time_category:
        result_time_category += "\"time_category_total"+"\" : \""+ str(len(time_category)) + "\", "
        for i in range(0,len(time_category)):
            # result_todo_category += "\"투두 카테고리 번호"+"\" : \""+ str(i+1) + "\", "
            if i == len(time_category)-1: # 마지막 줄이면 끝에 , 뺌
                result_time_category += "\"category_name"+str(i)+"\" : \""+ time_category[i].name + "\", " +"\"category_color"+str(i)+"\" : \""+ time_category[i].color +"\", " +"\"SUCCESS"+"\" : \""+ str(200) +"\""
            else: # 마지막 줄이 아니면 , 추가
                result_time_category += "\"category_name"+str(i)+"\" : \""+ time_category[i].name + "\", " +"\"category_color"+str(i)+"\" : \""+ time_category[i].color +"\", "
        result_time_category += "}"
        return json.loads(result_time_category)
    else:
        return statusCode.unexpected_error

# 타임 카테고리 수정을 위해 카테고리 색상 가져오는 메소드
@router.get("/get_time_category/{login_id}/{cName}/{isTodo}",status_code=200)
async def get_time_category(login_id: str, cName: str, isTodo: int, db:Session = Depends(get_db)):
    """
    타임 리스트 수정 화면에서 카테고리 수정하는 API
    """
    is_exist_userId = db.query(models.Users.id).filter_by(login_id=login_id).first()
    time_category_color = db.query(models.Category).filter_by(user_id = is_exist_userId.id, name=cName, isTodo=isTodo).first()

    if is_exist_userId == None:
        return statusCode.no_exist_user
    elif login_id == None:
        return statusCode.not_id
    elif cName == None:
        return statusCode.no_category_name
    elif isTodo == 1:
        return statusCode.isTodo_error
    elif time_category_color == None:
        return statusCode.no_category_color
    elif login_id and time_category_color:
        result = {"time_category_color":time_category_color.color, "SUCCESS": 200}
        return result
    else:
        return statusCode.unexpected_error