from models import Course
from sqlalchemy.orm import Session

class CourseService:
    def __init__(self, session: Session):
        self._db = session # private

    def get_course(self) -> list[Course]:
        return self._db.query(Course).all()