from fastapi import FastAPI
from typing import List, Annotated
import models
from database import engine, SessionLocal
from fastapi.middleware.cors import CORSMiddleware
from routers.courses import router as courses_router

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

origins = [
    'http://localhost:5173'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins
)

app.include_router(courses_router)

@app.get("/")
def read_root():
    return {"message": "Backend is running successfully!"}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
