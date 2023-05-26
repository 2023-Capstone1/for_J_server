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

router = APIRouter(prefix="/usersAPI",tags=["usersAPI"])

async def is_login_id_exist(login_id_str: str,db:Session = Depends(get_db)):
    # 같은 id가 있는지 확인하는 함수
    get_login_id = db.query(models.Users.login_id).filter_by(login_id=login_id_str).first()
    if get_login_id:
        return True
    else:
        return False

@router.post("/get_certification_number/{login_email}")
async def signup(login_email:str):
    """
    인증 이메일 발송 API
    """
    try:
        validate_email(login_email)
    except EmailNotValidError:
        raise HTTPException(status_code=400, detail="Invalid email address")

    token = create_email_verification_token(login_email)
    send_email_verification_email(login_email, token)

    return statusCode.success

@router.get("/verify_email/{token}",status_code=200)
async def verify_email(token: str, db:Session = Depends(get_db)):
    """
    이메일 인증
    """
    email = verify_email_verification_token(token)

    email_check = db.query(models.Users.login_email).filter_by(login_email = email).first()
    userId_check = db.query(models.Users.login_id).filter_by(login_email = email).first()
    certification_number = random.randint(100000, 999999)

    if email is None:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    elif userId_check: # ID가 db에 있을 경우
        db.query(models.Users).filter_by(login_email = email).update({"login_certification_number":certification_number})
        db.commit()
        return {"certification_number" : str(certification_number)}
    elif email_check: # 이메일이 db에 있을 경우
        db.query(models.Users).filter_by(login_email = email).update({"login_certification_number":certification_number})
        db.commit()
        return {"certification_number" : str(certification_number)}
    else: # 이메일이 db에 없는 경우
        models.Users.create(db, auto_commit = True, login_email = email, login_certification_number = certification_number)
        return {"certification_number" : str(certification_number)}

@router.get("/check_verification/{login_email}/{login_certification_number}",status_code=200)
async def verify_email(login_email: str, login_certification_number: int, db:Session = Depends(get_db)):
    """
    인증번호 확인 API
    """
    user = db.query(models.Users).filter_by(login_email = login_email).first()

    if user: # 해당 이메일을 가진 유저가 존재할 경우
        if user.login_certification_number == login_certification_number: # 인증번호가 일치할 경우
            return statusCode.success
        else:   
            return statusCode.certification_Number
    elif user == None:
        return statusCode.not_email
    else:
        return statusCode.unexpected_error
    
@router.post("/register/{login_id}/{login_pw}/{login_name}/{login_email}",status_code=200)
async def register(login_id: str, login_pw:str, login_name: str, login_email:str, db:Session = Depends(get_db)):
    """
    회원가입 API
    """
    is_exist_userId = db.query(models.Users.login_id).filter_by(login_id=login_id).first()
    is_exist_userEmail = db.query(models.Users.login_email).filter_by(login_email=login_email).first()
    user = db.query(models.Users).filter_by(login_id = login_id, login_pw = login_pw, login_name = login_name, login_email = login_email).first()


    if not login_id:
        return statusCode.signup_error
    elif not login_pw:
        return statusCode.signup_error
    elif is_exist_userEmail: # 이메일이 존재하면 이미 있는 행 지우고 해당 이메일 행 다시 생성
        db.query(models.Users).filter(models.Users.login_email == login_email).delete()
        db.commit()
        models.Users.create(db, auto_commit = True, login_id = login_id, login_pw = login_pw, login_name = login_name, login_email = login_email, login_certification_number = None)
        # 사용자 정보 등록 시 setting 테이블에 새로운 사용자의 알람 유무도 기본으로 등록함
        get_user = db.query(models.Users).filter_by(login_id = login_id, login_pw = login_pw, login_name = login_name, login_email = login_email).first()
        models.Setting.create(db, auto_commit = True, user_id = get_user.id, alarm_switch = 0, todo_time = "09:00", todo_switch = 0, habit_time = "09:00", habit_switch = 0, calendar_time = "09:00", calenbar_switch = 0, time_switch = 0)
        return statusCode.success
    elif is_exist_userId:
        return statusCode.id_duplication_error
    
    if user == None:
        models.Users.create(db, auto_commit = True, login_id = login_id, login_pw = login_pw, login_name = login_name, login_email = login_email, login_certification_number = None)
        # 사용자 정보 등록 시 setting 테이블에 새로운 사용자의 알람 유무도 기본으로 등록함
        get_user = db.query(models.Users).filter_by(login_id = login_id, login_pw = login_pw, login_name = login_name, login_email = login_email).first()
        models.Setting.create(db, auto_commit = True, user_id = get_user.id, alarm_switch = 0, todo_time = "09:00", todo_switch = 0, habit_time = "09:00", habit_switch = 0, calendar_time = "09:00", calenbar_switch = 0, time_switch = 0)
        return statusCode.success
    else:
        return statusCode.unexpected_error

@router.get("/id_check/{login_id}",status_code=200)
async def idcheck(login_id: str,db:Session = Depends(get_db)): 
    """
    아이디 중복 확인 API
    """
    is_exist = db.query(models.Users.login_id).filter_by(login_id=login_id).first()
    
    if is_exist:
        return statusCode.id_duplication_error
    elif None == is_exist:
        return statusCode.success
    else:
        return statusCode.unexpected_error

@router.get("/login/{login_id}/{login_pw}",status_code=200)
async def login(login_id: str, login_pw:str,db:Session = Depends(get_db)):
    """
    로그인 API
    """
    is_exist = await is_login_id_exist(login_id,db)
    user_info = db.query(models.Users).filter_by(login_id=login_id).first()

    if None == user_info:
        return statusCode.login_id_pw_error
    elif user_info.login_id != login_id and user_info.login_pw != login_pw:
        return statusCode.login_id_pw_error
    elif user_info.login_pw != login_pw:
        return statusCode.login_pw_error
    elif user_info.login_id != login_id:
        return statusCode.login_id_error
    elif is_exist == True:
        if user_info.login_id == login_id:
            return statusCode.success
    else:
        return statusCode.unexpected_error
    
@router.get("/logout/{login_id}/{login_pw}",status_code=200)
async def logout(login_id: str, login_pw:str,db:Session = Depends(get_db)):
    """
    로그아웃 API
    """
    now = datetime.datetime.now()
    
    get_user = db.query(models.Users).filter_by(login_id=login_id, login_pw=login_pw).first()

    if get_user:
        get_user.updated_at = now
        db.commit()
        return statusCode.success
    elif get_user == None:
        return statusCode.not_id_pw
    else:
        return statusCode.unexpected_error

@router.get("/id_find/{login_name}/{login_email}",status_code=200)
async def id_find(login_name: str, login_email:str, db:Session = Depends(get_db)):
    """
    ID 찾기 API
    """
    is_exist_name = db.query(models.Users.login_name).filter_by(login_name = login_name).first()
    is_exist_email = db.query(models.Users.login_email).filter_by(login_email = login_email).first()
    
    if is_exist_name and is_exist_email:
        user_id = db.query(models.Users.login_id).filter_by(login_name = login_name, login_email = login_email).first()
        result = {"user_id": user_id.login_id, "SUCCESS": 200}
        return result
    elif None == is_exist_name:
        return statusCode.not_name
    elif None == is_exist_email:
        return statusCode.not_email
    else:
        return statusCode.unexpected_error

@router.get("/user_info/{login_id}/",status_code=200)
async def user_info(login_id: str,db:Session = Depends(get_db)):
    """
    user_info
    """
    is_exist_user_info = db.query(models.Users).filter_by(login_id=login_id).first()
    
    if is_exist_user_info == None:
        return statusCode.not_id
    elif is_exist_user_info:
        result = {"user_id":is_exist_user_info.login_id, "user_pw": is_exist_user_info.login_pw, "user_name":is_exist_user_info.login_name, "user_email":is_exist_user_info.login_email, "status": 200}
        return result
    else:
        return statusCode.unexpected_error

@router.put("/pw_update/{login_id}/{new_user_pw}/{new_user_pw_check}",status_code=200)
async def pw_update(login_id: str, new_user_pw: str, new_user_pw_check: str, db:Session = Depends(get_db)):
    """
    본인 확인 후 PW 수정 API
    """
    get_id = db.query(models.Users.login_id).filter_by(login_id=login_id).first()
    get_pw = db.query(models.Users.login_pw).filter_by(login_id=login_id).first()

    if get_id and get_pw:
        db.query(models.Users).filter(models.Users.login_id == login_id).update({"login_pw":new_user_pw})
        db.commit()
        return statusCode.success
    elif None == get_id:
        return statusCode.not_id
    elif new_user_pw != new_user_pw_check:
        return statusCode.not_equal_new_pw
    return statusCode.unexpected_error

@router.delete("/user_delete/{login_id}/{login_pw}",status_code=200)
async def user_delete(login_id: str, login_pw:str, db:Session = Depends(get_db)):
    """
    계정 삭제 API
    """
    exist_user_id = db.query(models.Users).filter_by(login_id = login_id).first()
    exist_user_pw = db.query(models.Users.login_pw).filter_by(login_pw = login_pw).first()

    if exist_user_id and exist_user_pw:
        db.query(models.Users).filter(models.Users.login_pw == login_pw).delete()
        db.query(models.Setting).filter(models.Setting.user_id == exist_user_id.id).delete()
        db.commit()
        return statusCode.success
    elif None == exist_user_id:
        return statusCode.not_id
    elif None == exist_user_pw:
        return statusCode.login_pw_error    
    else:
        return statusCode.unexpected_error
