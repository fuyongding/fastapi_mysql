from fastapi import FastAPI, Path, Query, HTTPException, Depends
from sqlalchemy.orm import Session
import crud, database, models, schemas # this executes all the code in these files that are not functions,variables,....

app = FastAPI()

# person endpoints
@app.post("/persons", response_model=schemas.Person)
def create_person(person: schemas.PersonCreate, db: Session = Depends(database.get_db)):
    db_person = crud.get_person_by_name(db, person.name)
    if db_person:
        raise HTTPException(status_code=400, detail="Person with this name already registered")
    return crud.create_person(db=db, person=person)

@app.get("/persons", response_model=list[schemas.Person])
def get_all_persons(db: Session = Depends(database.get_db)):
    return crud.get_all_persons(db)

@app.get("/persons/{person_id}", response_model=schemas.Person)
def get_person_by_id(
    *, 
    db: Session = Depends(database.get_db), 
    person_id: int
):
    db_person = crud.get_person_by_id(db, person_id)
    if not db_person:
        raise HTTPException(status_code=404, detail="Person with this id does not exist")
    return db_person

@app.put("/persons/{person_id}", response_model=schemas.Person)
def update_person(
    *,
    person_id: int = Path(description="id of the person to get"), 
    person_update: schemas.PersonBase, 
    db: Session = Depends(database.get_db)
):
    updated_person = crud.update_person(db, person_id, person_update)
    if updated_person is None:
        raise HTTPException(status_code=404, detail="Person with this id does not exist")
    return updated_person

# task endpoints
@app.post("/tasks", response_model=schemas.Task)
def create_task(
    *, 
    task: schemas.TaskCreate, 
    db: Session = Depends(database.get_db), 
    person_id: int = Path(description="id of the person to update")
):
    db_person = crud.get_person_by_id(db, person_id)
    if not db_person:
        raise HTTPException(status_code=404, detail="Person with this id does not exist")
    return crud.create_task(db, task, person_id)

@app.get("/tasks", response_model=list[schemas.Task])
def get_all_tasks(db: Session = Depends(database.get_db)):
    return crud.get_all_tasks(db)

@app.get("/tasks/{task_id}", response_model=schemas.Task)
def get_task_by_id(
    *,
    task_id: int = Path(description="id of the task to get"), 
    db: Session = Depends(database.get_db)
):
    db_task = crud.get_task_by_id(db, task_id)
    if not db_task:
        raise HTTPException(status_code=400, detail="Task with this id does not exist") # bad request
    return db_task
   
@app.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(
    *, 
    task_id: int = Path(description="id of the task to update"), 
    task_update: schemas.TaskBase, 
    db: Session = Depends(database.get_db)
):
    updated_task = crud.update_task(db, task_id, task_update)
    if updated_task is None:
        raise HTTPException(status_code=404, detail="Task with this id does not exist")
    return updated_task

# @app.delete("/tasks/{task_id}", response_model=ResponseMessage)
# async def delete_task_by_id(
#     task_id: int= Path(description="id of the task to delete")
# ):
#     db = get_DB()
#     with db.cursor() as cursor:
#         query = "SELECT * FROM tasks WHERE id = %s"
#         cursor.execute(query, (task_id))
#         task = cursor.fetchone()
#         if task is None:
#             raise HTTPException(status_code=404, detail="Task not found")

#         query = "DELETE FROM tasks WHERE id = %s"
#         cursor.execute(query, (task_id))
#         db.commit()
#         return ResponseMessage(message="Task deleted")