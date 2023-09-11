"""
Crud methods 
"""
# pylint: disable=invalid-name
# pylint: disable=trailing-whitespace
from sqlalchemy.orm import Session
from model import models
from schema import schemas

def create_person(db: Session, person: schemas.PersonCreate):
    """create person method

    Args:
        db (Session): local db session
        person (schemas.PersonCreate): model for creating person

    Returns:
        Person: newly created person
    """
    db_person = models.Person(**person.model_dump())
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person

def get_all_persons(db: Session):
    """method to get all persons

    Args:
        db (Session): local db session

    Returns:
        list[Person]: list of all people
    """
    return db.query(models.Person).all()

def get_person_by_name(db: Session, name: str):
    """get person by name

    Args:
        db (Session): local db session
        name (str): name of person to get

    Returns:
        Person: queried person
    """
    db_person = db.query(models.Person).filter(models.Person.name == name).first()
    return db_person

def get_person_by_id(db: Session, person_id: int):
    """get person by id

    Args:
        db (Session): local db session
        person_id (int): id of person to get

    Returns:
        Person: queried person
    """
    db_person = db.query(models.Person).filter(models.Person.id == person_id).first()
    return db_person

def update_person(db: Session, person_id: int, person_update: schemas.PersonBase):
    """update person by id

    Args:
        db (Session): local db session
        person_id (int): id of person to update
        person_update (schemas.PersonBase): new details of person

    Returns:
        Person: person with updated details
    """
    existing_person = db.query(models.Person).filter(models.Person.id == person_id).first()

    if existing_person is None:
        return None 

    for attr, value in person_update.model_dump().items():
        setattr(existing_person, attr, value)
        
    db.commit()
    db.refresh(existing_person) 
    return existing_person

def delete_person(db: Session, person_id: int):
    """delete person by id

    Args:
        db (Session): local db session
        person_id (int): id of person to delete

    Returns:
        boolean: True if delete success, else False
    """
    existing_person = db.query(models.Person).filter(models.Person.id == person_id).first()
    if existing_person:
        # delete tasks assigned to person before deleting the person
        for task in existing_person.tasks:
            print(task)
            delete_task(db, task.id)
        db.delete(existing_person)
        db.commit()
        return True
    return False

def create_task(db: Session, task: schemas.TaskCreate, person_id: int):
    """create new task

    Args:
        db (Session): local db session
        task (schemas.TaskCreate): task to create
        person_id (int): id of assigned person

    Returns:
        Task: newly created task
    """
    db_task = models.Task(**task.model_dump(), assigned_person_id = person_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_all_tasks(db: Session):
    """get all tasks

    Args:
        db (Session): local db session

    Returns:
        list[Task]: list of all tasks
    """
    return db.query(models.Task).all()

def get_task_by_id(db: Session, task_id: int):
    """get task by id

    Args:
        db (Session): local db session
        task_id (int): id of task to get

    Returns:
        Task: queried task
    """
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    return db_task

def update_task(db: Session, task_id: int, task_update: schemas.PersonBase):
    """update task based on task id

    Args:
        db (Session): local db session
        task_id (int): 
        task_update (schemas.PersonBase): new task

    Returns:
        Task: task with updated details
    """
    existing_task = db.query(models.Task).filter(models.Task.id == task_id).first()

    if existing_task is None:
        return None 

    for attr, value in task_update.model_dump().items():
        setattr(existing_task, attr, value)
        
    db.commit()
    db.refresh(existing_task) 
    return existing_task

def delete_task(db: Session, task_id: int):
    """delete task by id

    Args:
        db (Session): local db session
        task_id (int): id of task to delete

    Returns:
        Boolean: True if task deleted successfully, else false
    """
    existing_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if existing_task:
        db.delete(existing_task)
        db.commit()
        return True
    return False
