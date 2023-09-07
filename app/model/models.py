"""
Models to be used in ORM
"""
# pylint: disable=too-few-public-methods
from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, Date
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Task(Base):
    """Task table

    Args:
        Base (_type_): _description_
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30), index=True)
    description = Column(String(60), index=True)
    completed = Column(Boolean, default=False)
    startdate = Column(Date, nullable=True)
    enddate = Column(Date, nullable=True)
    assigned_person_id = Column(Integer, ForeignKey("persons.id"))

    # Define a foreign key relationship to the Person model
    assigned_person = relationship("Person", back_populates="tasks")

class Person(Base):
    """Person table

    Args:
        Base (_type_): _description_
    """
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)

    # Establish a one-to-many relationship with Task
    tasks = relationship("Task", back_populates="assigned_person")
