from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

students= []

class Student(BaseModel):
    name : str
    age : int
    course : str

@app.post("/students")
def add_students(student:Student):
    students.append(student.model_dump())
    return{
        "message" : "Added student successfully"
    }

@app.get("/view")
def view_student():
    return students
