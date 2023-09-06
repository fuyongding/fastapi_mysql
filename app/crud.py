from sqlalchemy.orm import Session
import models, schemas

# Person methods
def create_person(db: Session, person: schemas.PersonCreate):
    db_person = models.Person(**person.dict())
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person

def get_all_persons(db: Session):
    return db.query(models.Person).all()

def get_person_by_name(db: Session, name: str):
    db_person = db.query(models.Person).filter(models.Person.name == name).first()
    return db_person

def get_person_by_id(db: Session, person_id: int):
    db_person = db.query(models.Person).filter(models.Person.id == person_id).first()
    return db_person

def update_person(db: Session, person_id: int, person_update: schemas.PersonBase):
    existing_person = db.query(models.Person).filter(models.Person.id == person_id).first()

    if existing_person is None:
        return None 

    for attr, value in person_update.dict().items():
        setattr(existing_person, attr, value)
        
    db.commit()
    db.refresh(existing_person) 
    return existing_person

# Task methods
def create_task(db: Session, task: schemas.TaskCreate, person_id: int):
    db_task = models.Task(**task.dict(), assigned_person_id = person_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_all_tasks(db: Session):
    return db.query(models.Task).all()

def get_task_by_id(db: Session, task_id: str):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    return db_task

def update_task(db: Session, task_id: int, task_update: schemas.PersonBase):
    existing_task = db.query(models.Task).filter(models.Task.id == task_id).first()

    if existing_task is None:
        return None 

    for attr, value in task_update.dict().items():
        setattr(existing_task, attr, value)
        
    db.commit()
    db.refresh(existing_task) 
    return existing_task