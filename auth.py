from sqlalchemy.orm import Session
import models


def authenticate_user(db: Session, username: str, password: str):

    # check student
    student = db.query(models.Student).filter(
        models.Student.username == username,
        models.Student.password == password
    ).first()

    if student:
        return {
            "role": "student",
            "student_id": student.id
        }

    # check admin
    admin = db.query(models.Admin).filter(
        models.Admin.username == username,
        models.Admin.password == password
    ).first()

    if admin:
        return {
            "role": "admin"
        }

    return None