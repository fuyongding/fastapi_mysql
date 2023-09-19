"""
Main module that provides the crud endpoints for the webservice
"""
# pylint: disable=invalid-name
# pylint: disable=trailing-whitespace
import os
from fastapi import FastAPI, Path, Query, HTTPException, Depends, status
from sqlalchemy.orm import Session
from datetime import datetime
from .schemas import TaskBase, TaskCreate, Task, PersonBase, PersonCreate, Person
from .database import get_db
from .services.person_service import person_service
from .services.task_service import task_service

app = FastAPI()


@app.post("/persons", response_model=Person, status_code=status.HTTP_201_CREATED)
def create_person(person: PersonCreate, db: Session = Depends(get_db)) -> Person:
    """POST endpoint for person

    Args:
        person (PersonCreate): person to create
        db (Session): local database session

    Returns:
        Person: newly created person
    """
    if not person.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Person name cannot be empty!",
        )
    if len(person.name) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Person name is too long!"
        )

    db_person = person_service.get_person_by_name(name=person.name, db=db)
    if db_person:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Person with this name already registered",
        )

    return person_service.create_new_person(person=person, db=db)


@app.get("/persons", response_model=list[Person])
def get_all_persons(db: Session = Depends(get_db)) -> list[Person]:
    """GET endpoint to get all persons

    Args:
        db (Session): local database session

    Returns:
        list[Person]: a list of all persons
    """
    response = person_service.get_all_persons(db=db)
    return response


@app.get("/persons/{person_id}", response_model=Person)
def get_person_by_id(*, db: Session = Depends(get_db), person_id: int) -> Person:
    """GET endpoint to get person by id

    Args:
        db (Session): local database session
        person_id (int): id of person

    Returns:
        Person: person with the id specified
    """
    db_person = person_service.get_person_by_id(person_id=person_id, db=db)
    if not db_person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person with this id does not exist",
        )
    return db_person


@app.put("/persons/{person_id}", response_model=Person)
def update_person_by_id(
    *,
    person_id: int = Path(description="id of the person to update"),
    person_update: PersonBase,
    db: Session = Depends(get_db)
) -> Person:
    """PUT endpoint to update person

    Args:
        person_id (int): id of person
        person_update (PersonBase): PersonBase for update
        db (Session): local database session

    Returns:
        Person: updated person
    """
    if not person_update.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Person name cannot be empty!",
        )
    if len(person_update.name) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Person name is too long!"
        )

    updated_person = person_service.update_person_by_id(
        person_id=person_id, person_update=person_update, db=db
    )
    if updated_person is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person with this id does not exist",
        )
    return updated_person


@app.delete("/persons/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_person_by_id(person_id: int, db: Session = Depends(get_db)):
    """DELETE endpoint to delete person

    Args:
        person_id (int): id of person to delete
        db (Session): local database session

    Returns:
        Dict: message that person is deleted
    """
    delete_success = person_service.delete_person_by_id(person_id=person_id, db=db)
    if not delete_success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Person not found"
        )


# ------------------------------------------------------------------------------------------


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(
    *,
    task: TaskCreate,
    db: Session = Depends(get_db),
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
    if not task.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Task name cannot be empty!"
        )
    if len(task.name) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Task name is too long!"
        )
    if not task.startdate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task start date cannot be null!",
        )
    if len(task.description) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task description is too long!",
        )
    if (task.completed and not task.enddate) or (task.enddate and not task.completed):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="enddate and completed values are invalid!",
        )
    db_person = person_service.get_person_by_id(db=db, person_id=person_id)
    if not db_person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="no person with the id specified",
        )

    try:
        start_date = datetime.strptime(str(task.startdate), "%Y-%m-%d")
        if task.enddate:
            end_date = datetime.strptime(str(task.enddate), "%Y-%m-%d")
            if start_date > end_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="End date must be later than start date",
                )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid date format. Use YYYY-MM-DD format for dates.",
        )

    return task_service.create_new_task(db=db, task=task, person_id=person_id)


@app.get("/tasks", response_model=list[Task])
def get_all_tasks(db: Session = Depends(get_db)):
    """GET endpoint to get all tasks

    Args:
        db (Session): local database session

    Returns:
        list[Person]: a list of all tasks
    """
    return task_service.get_all_tasks(db=db)


@app.get("/tasks/{task_id}", response_model=Task)
def get_task_by_id(
    *,
    task_id: int = Path(description="id of the task to get"),
    db: Session = Depends(get_db)
):
    """GET endpoint to get task by id

    Args:
        db (Session): local database session
        task_id (int): id of task

    Returns:
        Task: task with the id specified
    """
    db_task = task_service.get_task_by_id(db=db, task_id=task_id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task with this id does not exist",
        )
    return db_task


@app.put("/tasks/{task_id}", response_model=Task)
def update_task_by_id(
    *,
    task_id: int = Path(description="id of the task to update"),
    task_update: TaskBase,
    db: Session = Depends(get_db)
):
    """PUT endpoint to update task

    Args:
        task_id (int): id of task
        task_update (TaskBase): TaskBase for update
        db (Session): local database session

    Returns:
        Task: updated task
    """
    if not task_update.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Task name cannot be empty!"
        )
    if len(task_update.name) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Task name is too long!"
        )
    if not task_update.startdate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task start date cannot be null!",
        )
    if len(task_update.description) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task description is too long!",
        )
    if (task_update.completed and not task_update.enddate) or (
        task_update.enddate and not task_update.completed
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="enddate and completed values are invalid!",
        )

    try:
        start_date = datetime.strptime(str(task_update.startdate), "%Y-%m-%d")
        if task_update.enddate:
            end_date = datetime.strptime(str(task_update.enddate), "%Y-%m-%d")
            if start_date > end_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="End date must be later than start date",
                )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid date format. Use YYYY-MM-DD format for dates.",
        )

    updated_task = task_service.update_task_by_id(
        db=db, task_id=task_id, task_update=task_update
    )
    if updated_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task with this id does not exist",
        )
    return updated_task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_by_id(task_id: int, db: Session = Depends(get_db)):
    """DELETE endpoint to delete task

    Args:
        task_id (int): id of task to delete
        db (Session): local database session
    """
    delete_success = task_service.delete_task_by_id(db=db, task_id=task_id)
    if not delete_success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Task not found"
        )
