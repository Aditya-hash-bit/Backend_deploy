from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import joblib
import numpy as np

app = FastAPI()

# ------------------ CORS (IMPORTANT) ------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ LOAD MODEL ------------------
model = joblib.load("ml_model.pkl")

# ------------------ DATABASE CONNECTION ------------------
conn = sqlite3.connect("students.db", check_same_thread=False)
cursor = conn.cursor()

# ------------------ CREATE TABLES ------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS students(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
usn TEXT,
username TEXT,
password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS predictions(
id INTEGER PRIMARY KEY AUTOINCREMENT,
student_id INTEGER,
attendance REAL,
study_hours REAL,
marks REAL,
assignment_score REAL,
gpa REAL,
result TEXT
)
""")

conn.commit()

# ------------------ HOME ------------------
@app.get("/")
def home():
    return {"message": "API is working successfully 🚀"}

# ------------------ LOGIN ------------------
@app.post("/login")
def login(data: dict):

    username = data.get("username")
    password = data.get("password")

    if username == "admin" and password == "admin123":
        return {"role": "admin"}

    cursor.execute(
        "SELECT id FROM students WHERE username=? AND password=?",
        (username, password)
    )

    student = cursor.fetchone()

    if student:
        return {"role": "student", "student_id": student[0]}

    return {"error": "Invalid credentials"}

# ------------------ REGISTER ------------------
@app.post("/register_student")
def register_student(data: dict):

    cursor.execute(
        "INSERT INTO students(name,usn,username,password) VALUES(?,?,?,?)",
        (data["name"], data["usn"], data["username"], data["password"])
    )

    conn.commit()

    return {"message": "Student registered successfully"}

# ------------------ GET STUDENTS ------------------
@app.get("/students")
def get_students():

    cursor.execute("SELECT id,name,usn,username FROM students")
    rows = cursor.fetchall()

    return [
        {
            "id": r[0],
            "name": r[1],
            "usn": r[2],
            "username": r[3]
        }
        for r in rows
    ]

# ------------------ PREDICT ------------------
@app.post("/predict")
def predict(data: dict):

    try:
        student_id = data["student_id"]

        attendance = float(data["attendance"])
        study_hours = float(data["study_hours"])
        marks = float(data["marks"])
        assignment_score = float(data["assignment_score"])
        gpa = float(data["gpa"])

        # Rule-based check
        if attendance < 75 or marks < 40 or gpa < 4.5:
            result = "Fail"
        else:
            features = np.array([[attendance, study_hours, marks, assignment_score, gpa]])
            prediction = model.predict(features)[0]
            result = "Pass" if prediction == 1 else "Fail"

        # Save to DB
        cursor.execute("""
        INSERT INTO predictions
        (student_id,attendance,study_hours,marks,assignment_score,gpa,result)
        VALUES(?,?,?,?,?,?,?)
        """,
        (student_id, attendance, study_hours, marks, assignment_score, gpa, result)
        )

        conn.commit()

        return {"prediction": result}

    except Exception as e:
        print("Prediction Error:", e)
        return {"error": "Prediction failed"}

# ------------------ HISTORY ------------------
@app.get("/prediction_history/{student_id}")
def prediction_history(student_id: int):

    cursor.execute("""
    SELECT attendance,study_hours,marks,assignment_score,gpa,result
    FROM predictions
    WHERE student_id=?
    """, (student_id,))

    rows = cursor.fetchall()

    return [
        {
            "attendance": r[0],
            "study_hours": r[1],
            "marks": r[2],
            "assignment_score": r[3],
            "gpa": r[4],
            "result": r[5]
        }
        for r in rows
    ]

# ------------------ DASHBOARD ------------------
@app.get("/dashboard_stats")
def dashboard_stats():

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.execute("""
    SELECT student_id, result
    FROM predictions
    WHERE id IN (
        SELECT MAX(id)
        FROM predictions
        GROUP BY student_id
    )
    """)

    rows = cursor.fetchall()

    pass_count = sum(1 for r in rows if r[1] == "Pass")
    fail_count = sum(1 for r in rows if r[1] == "Fail")

    total = pass_count + fail_count

    pass_rate = round((pass_count / total) * 100, 2) if total > 0 else 0
    fail_rate = round((fail_count / total) * 100, 2) if total > 0 else 0

    return {
        "total_students": total_students,
        "pass_rate": pass_rate,
        "fail_rate": fail_rate,
        "model_accuracy": 90
    }

# ------------------ FEEDBACK ------------------
@app.get("/student_feedback/{student_id}")
def student_feedback(student_id: int):

    cursor.execute("""
    SELECT attendance,study_hours,marks,assignment_score,gpa
    FROM predictions
    WHERE student_id=?
    """, (student_id,))

    rows = cursor.fetchall()

    if len(rows) == 0:
        return {"rating": "No Data", "feedback": ["Start predicting your performance."]}

    attendance = [r[0] for r in rows]
    study_hours = [r[1] for r in rows]
    marks = [r[2] for r in rows]
    assignment = [r[3] for r in rows]
    gpa = [r[4] for r in rows]

    avg_attendance = sum(attendance) / len(attendance)
    avg_study = sum(study_hours) / len(study_hours)
    avg_marks = sum(marks) / len(marks)
    avg_assignment = sum(assignment) / len(assignment)
    avg_gpa = sum(gpa) / len(gpa)

    feedback = []

    feedback.append("Improve attendance" if avg_attendance < 75 else "Good attendance")
    feedback.append("Study more" if avg_study < 3 else "Good study habits")
    feedback.append("Improve marks" if avg_marks < 60 else "Good marks")
    feedback.append("Improve assignments" if avg_assignment < 5 else "Good assignments")

    if avg_gpa >= 8:
        rating = "Excellent"
    elif avg_gpa >= 6:
        rating = "Good"
    elif avg_gpa >= 4.5:
        rating = "Average"
    else:
        rating = "Needs Improvement"

    return {
        "rating": rating,
        "feedback": feedback
    }