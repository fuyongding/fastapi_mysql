from pydantic import BaseModel
from datetime import date

# Base: for updates
# Create: for creates
# Task/Person: for response

# (Update Input Model)
class TaskBase(BaseModel):
    name: str
    description: str
    completed: bool
    startdate: date | None = None
    enddate: date | None = None

# (Create Input Model)
class TaskCreate(TaskBase):
    pass

# (Response Model)
class Task(TaskBase):
    id: int
    assigned_person_id: int

    class Config:
        orm_mode = True

class PersonBase(BaseModel):
    name: str

class PersonCreate(PersonBase):
    pass

class Person(PersonBase):
    id: int
    tasks: list[Task] = []

    class Config:
        orm_mode = True