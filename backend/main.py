from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from decimal import Decimal

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

class CourseBase(BaseModel):
    name: str
    credits: int

class ClassBase(BaseModel):
    course_id: int
    teacher: str
    capacity: int
    registered: int
    tuition: Decimal
    schedule: str 

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
