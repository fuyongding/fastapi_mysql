"""
Schemas for task
"""
# pylint: disable=too-few-public-methods
# pylint: disable=unnecessary-pass
from datetime import date
from pydantic import BaseModel, ConfigDict

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
    model_config = ConfigDict(from_attributes=True)