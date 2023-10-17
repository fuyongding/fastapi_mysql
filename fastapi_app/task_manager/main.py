"""
Main module that provides the crud endpoints for the webservice
"""
# pylint: disable=invalid-name
# pylint: disable=trailing-whitespace
from fastapi import FastAPI, Path, Query, HTTPException, Depends, status
from sqlalchemy.orm import Session
from datetime import datetime
from .schemas.persons import PersonBase, PersonCreate, Person
from .schemas.tasks import TaskBase, TaskCreate, Task
from .services.person_service import person_service
from .services.task_service import task_service
from .db.database import get_db

app = FastAPI()

@app.post("/persons", response_model=Person, status_code=status.HTTP_201_CREATED)
def create_person(person: PersonCreate, db: Session = Depends(get_db)) -> Person:
    """POST endpoint for person

    Args:
        person (PersonCreate): person to create

    Returns:
        Person: newly created person
    """
    return person_service.create_new_person(person=person, db=db)


@app.get("/persons", response_model=list[Person])
def get_all_persons(db: Session = Depends(get_db)) -> list[Person]:
    """GET endpoint to get all persons

    Returns:
        list[Person]: a list of all persons
    """
    return person_service.get_all_persons(db=db)


@app.get("/persons/{person_id}", response_model=Person)
def get_person_by_id(*, db: Session = Depends(get_db), person_id: int) -> Person:
    """GET endpoint to get person by id

    Args:
        person_id (int): id of person

    Returns:
        Person: person with the id specified
    """
    return person_service.get_person_by_id(person_id=person_id, db=db)


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

    Returns:
        Person: updated person
    """
    return person_service.update_person_by_id(
        person_id=person_id, person_update=person_update, db=db
    )


@app.delete("/persons/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_person_by_id(person_id: int, db: Session = Depends(get_db)):
    """DELETE endpoint to delete person

    Args:
        person_id (int): id of person to delete

    Returns:
        Dict: message that person is deleted
    """
    return person_service.delete_person_by_id(person_id=person_id, db=db)


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
        person_id (int): id of the assigned person

    Returns:
        Task: newly created task
    """
    return task_service.create_new_task(db=db, task=task, person_id=person_id)


@app.get("/tasks", response_model=list[Task])
def get_all_tasks(db: Session = Depends(get_db)):
    """GET endpoint to get all tasks

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
        task_id (int): id of task

    Returns:
        Task: task with the id specified
    """
    return task_service.get_task_by_id(db=db, task_id=task_id)


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

    Returns:
        Task: updated task
    """
    return task_service.update_task_by_id(
        db=db, task_id=task_id, task_update=task_update
    )


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_by_id(task_id: int, db: Session = Depends(get_db)):
    """DELETE endpoint to delete task

    Args:
        task_id (int): id of task to delete
    """
    return task_service.delete_task_by_id(db=db, task_id=task_id)

# ------------------------------------------------------------------------------------------

@app.on_event("shutdown")
def shutdown_event():
    rabbitmq_service.close()
