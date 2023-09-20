"""
Schemas for persons
"""
# pylint: disable=too-few-public-methods
# pylint: disable=unnecessary-pass
from .tasks import Task
from pydantic import BaseModel, ConfigDict

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
    model_config = ConfigDict(from_attributes=True)