from sqlalchemy.orm import Session
from models import Task

def get_all_tasks(db: Session):
    return db.query(Task).all()

