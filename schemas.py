from pydantic import BaseModel, Field


class Login(BaseModel):

    username: str
    password: str


class StudentCreate(BaseModel):

    name: str
    usn: str
    username: str
    password: str


class PredictionInput(BaseModel):

    student_id: int
    attendance: float
    study_hours: float
    marks: float
    assignment: int = Field(..., ge=1, le=10)
    gpa: float