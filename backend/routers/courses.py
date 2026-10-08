from services.course_service import CourseService
from schemas import CourseBase
from database import SessionLocal
from fastapi import APIRouter, Depends, HTTPException


router = APIRouter()

def get_course_service() -> CourseService:
    return CourseService(session=SessionLocal())

@router.get("/courses", response_model=list[CourseBase])
def get_courses(service: CourseService = Depends(get_course_service)):
    return service.get_course()
