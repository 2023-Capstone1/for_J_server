from fastapi import APIRouter, FastAPI, HTTPException
from requests import Session
from fastapi.params import Depends
from db import get_db

import models, datetime, random, statusCode
import json

router = APIRouter(prefix="/hardwareAPI",tags=["hardwareAPI"])

@router.get("/progress/{login_id}/",status_code=200)
async def user_info(login_id: str,db:Session = Depends(get_db)):
    """
    현재 진행도 확인 API
    """
    is_exist_user_info = db.query(models.Users).filter_by(login_id=login_id).first()
    
    if is_exist_user_info == None:
        return statusCode.not_id
    elif is_exist_user_info:
        result = 50
        return result
    else:
        return statusCode.unexpected_error 