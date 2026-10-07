from database import SessionLocal
from models import Course

db = SessionLocal()

courses = [
    Course(name="Database Systems", credits=3),
    Course(name="Computer Networks", credits=3),
    Course(name="Operating Systems", credits=4),
    Course(name="Software Engineering", credits=3),
]

db.add_all(courses)
db.commit()
db.close()