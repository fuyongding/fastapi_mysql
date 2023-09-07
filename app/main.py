"""
Main module that provides the crud endpoints for the webservice
"""
# pylint: disable=invalid-name
# pylint: disable=trailing-whitespace
from fastapi import FastAPI, Path, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from crud import crud
from database import database
from schema import schemas

app = FastAPI()

@app.get("/", response_model=dict)
def root_route():
    """root route for app
    """
    return {"hello":"world"}

@app.post("/persons", response_model=schemas.Person)
def create_person(person: schemas.PersonCreate, db: Session = Depends(database.get_db)):
    """POST endpoint for person

    Args:
        person (PersonCreate): person to create
        db (Session): local database session
    
    Returns:
        Person: newly created person
    """
    db_person = crud.get_person_by_name(db, person.name)
    if db_person:
        raise HTTPException(status_code=400, detail="Person with this name already registered")
    return crud.create_person(db=db, person=person)

@app.get("/persons", response_model=list[schemas.Person])
def get_all_persons(db: Session = Depends(database.get_db)):
    """GET endpoint to get all persons

    Args:
        db (Session): local database session
    
    Returns:
        list[Person]: a list of all persons
    """
    return crud.get_all_persons(db)

@app.get("/persons/{person_id}", response_model=schemas.Person)
def get_person_by_id(
    *, 
    db: Session = Depends(database.get_db), 
    person_id: int
):
    """GET endpoint to get person by id

    Args:
        db (Session): local database session
        person_id (int): id of person
    
    Returns:
        Person: person with the id specified
    """
    db_person = crud.get_person_by_id(db, person_id)
    if not db_person:
        raise HTTPException(status_code=404, detail="Person with this id does not exist")
    return db_person

@app.put("/persons/{person_id}", response_model=schemas.Person)
def update_person(
    *,
    person_id: int = Path(description="id of the person to update"), 
    person_update: schemas.PersonBase, 
    db: Session = Depends(database.get_db)
):
    """PUT endpoint to update person

    Args:
        person_id (int): id of person
        person_update (PersonBase): PersonBase for update
        db (Session): local database session
    
    Returns:
        Person: updated person
    """
    updated_person = crud.update_person(db, person_id, person_update)
    if updated_person is None:
        raise HTTPException(status_code=404, detail="Person with this id does not exist")
    return updated_person

@app.delete("/persons/{person_id}", response_model=dict)
def delete_person(person_id: int, db: Session = Depends(database.get_db)):
    """DELETE endpoint to delete person

    Args:
        person_id (int): id of person to delete
        db (Session): local database session
    
    Returns:
        Dict: message that person is deleted
    """
    delete_success = crud.delete_person(db, person_id)
    if not delete_success:
        raise HTTPException(status_code=404, detail="Person not found")
    return {"message": "Person deleted"}

@app.post("/tasks", response_model=schemas.Task)
def create_task(
    *, 
    task: schemas.TaskCreate, 
    db: Session = Depends(database.get_db), 
    person_id: int = Query(description="id of the person to assign this task to")
):
    """POST endpoint for tasks

    Args:
        task (TaskCreate): task to create
        db (Session): local database session
        person_id (int): id of the assigned person
    
    Returns:
        Task: newly created task
    """
    db_person = crud.get_person_by_id(db, person_id)
    if not db_person:
        raise HTTPException(status_code=404, detail="Person with this id does not exist")
    return crud.create_task(db, task, person_id)

@app.get("/tasks", response_model=list[schemas.Task])
def get_all_tasks(db: Session = Depends(database.get_db)):
    """GET endpoint to get all tasks

    Args:
        db (Session): local database session
    
    Returns:
        list[Person]: a list of all tasks
    """
    return crud.get_all_tasks(db)

@app.get("/tasks/{task_id}", response_model=schemas.Task)
def get_task_by_id(
    *,
    task_id: int = Path(description="id of the task to get"), 
    db: Session = Depends(database.get_db)
):
    """GET endpoint to get task by id

    Args:
        db (Session): local database session
        task_id (int): id of task
    
    Returns:
        Task: task with the id specified
    """
    db_task = crud.get_task_by_id(db, task_id)
    if not db_task:
        # 400: bad request
        raise HTTPException(
            status_code=400, 
            detail="Task with this id does not exist"
            ) 
    return db_task
   
@app.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(
    *, 
    task_id: int = Path(description="id of the task to update"), 
    task_update: schemas.TaskBase, 
    db: Session = Depends(database.get_db)
):
    """PUT endpoint to update task

    Args:
        task_id (int): id of task
        task_update (TaskBase): TaskBase for update
        db (Session): local database session
    
    Returns:
        Task: updated task
    """
    updated_task = crud.update_task(db, task_id, task_update)
    if updated_task is None:
        raise HTTPException(
            status_code=404, 
            detail="Task with this id does not exist"
        )
    return updated_task

@app.delete("/tasks/{task_id}", response_model=dict)
def delete_task(task_id: int, db: Session = Depends(database.get_db)):
    """DELETE endpoint to delete task

    Args:
        task_id (int): id of task to delete
        db (Session): local database session
    
    Returns:
        Dict: message that task is deleted
    """ 
    delete_success = crud.delete_task(db, task_id)
    if not delete_success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted"}
