from pydantic import BaseModel
from decimal import Decimal

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