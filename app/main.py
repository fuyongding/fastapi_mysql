import os
from fastapi import FastAPI, Path, Query, HTTPException, Depends
from sqlalchemy.orm import Session
import crud, database, models, schemas

app = FastAPI()

@app.post("/tasks", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(database.get_db)):
    return crud.create_task(db, task)

@app.get("/tasks", response_model=list[schemas.Task])
def get_tasks(db: Session = Depends(database.get_db)):
    return crud.get_all_tasks(db)

# @app.get("/tasks/{task_id}", response_model=Task)
# async def get_task_by_id(
#     task_id: int = Path(description="id of the task to get")
# ):
#     db = get_DB()
#     with db.cursor() as cursor:
#         query = "SELECT * FROM tasks WHERE id = %s"
#         cursor.execute(query, (task_id))
#         task = cursor.fetchone()
#         if task is None:
#             raise HTTPException(status_code=404, detail="Task not found")
#         return task

# @app.get("/tasks/by_name/", response_model=Task)
# async def get_task_by_name(
#     name: str = Query(description="Name of the task to get")
# ):
#     db = get_DB()
#     with db.cursor() as cursor:
#         query = "SELECT * FROM tasks WHERE name = %s"
#         cursor.execute(query, (name,))
#         task = cursor.fetchone()
#         if task is None:
#             raise HTTPException(status_code=404, detail="Task not found")
#         return task
 
# @app.put("/tasks/{task_id}", response_model=Task | ResponseMessage)
# async def update_task_by_id(
#     *, 
#     task_id: int = Path(description="id of the task to update"), 
#     updated_task: Task
# ):
#     db = get_DB()
#     update_values = []
#     with db.cursor() as cursor:
#         query = "SELECT * FROM tasks WHERE id = %s"
#         cursor.execute(query, (task_id,))
#         find_task = cursor.fetchone()
#         if find_task is None:
#             raise HTTPException(status_code=404, detail="Task not found")

#         query = "SELECT id FROM tasks WHERE name = %s AND id != %s"
#         cursor.execute(query, (updated_task.name, task_id))
#         existing_task = cursor.fetchone()
#         if existing_task:
#             return ResponseMessage(message="Task already exists with the same name")

#         query = "UPDATE tasks SET"
#         if updated_task.name:
#             query += " name = %s,"
#             update_values.append(updated_task.name)
#         if updated_task.description:
#             query += " description = %s,"
#             update_values.append(updated_task.description)
#         if updated_task.completed is not None:
#             query += " completed = %s,"
#             update_values.append(updated_task.completed)
#         if updated_task.startdate:
#             query += " startdate = %s,"
#             update_values.append(updated_task.startdate)
#         if updated_task.enddate:
#             query += " enddate = %s,"
#             update_values.append(updated_task.enddate)  

#         # Remove the trailing comma and complete the query
#         query = query.rstrip(",") + " WHERE id = %s"
#         update_values.append(task_id)

#         cursor.execute(query, update_values)
#         db.commit()

#         # Retrieve the updated task from the database
#         updated_query = "SELECT * FROM tasks WHERE id = %s"
#         cursor.execute(updated_query, (task_id))
#         task = cursor.fetchone()

#         return task

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