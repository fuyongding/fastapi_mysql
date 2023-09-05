from sqlalchemy import Column, Integer, String, Boolean, Date
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(16), index=True)
    description = Column(String(60), index=True)
    completed = Column(Boolean, default=False)
    startdate = Column(Date, nullable=True)
    enddate = Column(Date, nullable=True)

class ResponseMessage(BaseModel):
    message: str