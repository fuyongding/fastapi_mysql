"""
Defined schemas
"""
# pylint: disable=too-few-public-methods
# pylint: disable=unnecessary-pass
# pylint: disable=missing-class-docstring
from datetime import date
from pydantic import BaseModel

class TaskBase(BaseModel):
    """Schema for task updates
    """
    name: str
    description: str
    completed: bool
    startdate: date | None = None
    enddate: date | None = None

class TaskCreate(TaskBase):
    """Schema for task create
    """
    pass

class Task(TaskBase):
    """Schema for Task response model
    """
    id: int
    assigned_person_id: int

    class Config:
        orm_mode = True

class PersonBase(BaseModel):
    """Schema for person updates
    """
    name: str

class PersonCreate(PersonBase):
    """Schema for person create
    """
    pass

class Person(PersonBase):
    """Schema for Person response model
    """
    id: int
    tasks: list[Task] = []

    class Config:
        orm_mode = True
