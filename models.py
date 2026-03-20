from sqlalchemy import Column,Integer,String,Float
from database import Base

class Admin(Base):

    __tablename__ = "admins"

    id = Column(Integer,primary_key=True)
    username = Column(String)
    password = Column(String)


class Student(Base):

    __tablename__ = "students"

    id = Column(Integer,primary_key=True)
    name = Column(String)
    usn = Column(String)
    username = Column(String)
    password = Column(String)


class Prediction(Base):

    __tablename__ = "predictions"

    id = Column(Integer,primary_key=True)

    student_id = Column(Integer)

    attendance = Column(Float)
    study_hours = Column(Float)
    marks = Column(Float)
    assignment = Column(Float)
    gpa = Column(Float)

    prediction = Column(String)