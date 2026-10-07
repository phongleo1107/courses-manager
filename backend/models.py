from sqlalchemy import Column, ForeignKey, Integer, String, Numeric
from database import Base

class Course(Base):
    __tablename__ = 'courses'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    credits = Column(Integer, index=True)

class Class(Base):
    __tablename__ = 'classes'

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(
        Integer,
        ForeignKey("courses.id")
    )
    class_code = Column(String, unique=True)
    teacher = Column(String)
    capacity = Column(Integer)
    registered = Column(Integer)
    tuition = Column(Numeric(10, 2))
    schedule = Column(String)