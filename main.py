import uvicorn
from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from starlette.responses import RedirectResponse
from requests import sessions
from fastapi.params import Depends

import models, schemas, usersAPI, todoAPI, categoryAPI, timeAPI, habitAPI, checkAPI, hardwareAPI, settingAPI, calendarAPI, test, daTest, minTest

from datetime import timedelta, datetime

from db import enigne, get_db
models.Base.metadata.create_all(bind=enigne)

# python main.py ip port 
app = FastAPI()

app.include_router(usersAPI.router)
app.include_router(todoAPI.router)
app.include_router(categoryAPI.router)
app.include_router(timeAPI.router)
app.include_router(habitAPI.router)
app.include_router(checkAPI.router)
app.include_router(hardwareAPI.router)
app.include_router(settingAPI.router)
app.include_router(calendarAPI.router)
app.include_router(test.router)

app.include_router(daTest.router)
app.include_router(minTest.router)

@app.get("/")
def main():
    return RedirectResponse(url="/docs")