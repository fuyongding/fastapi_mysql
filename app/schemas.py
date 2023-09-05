from pydantic import BaseModel
from datetime import date

class TaskBase(BaseModel):
    name: str
    description: str
    completed: bool
    startdate: date | None = None
    enddate: date | None = None

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: int

    class Config:
        orm_mode = True