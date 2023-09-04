import os
from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel
from datetime import date

import pymysql

app = FastAPI()

# connect to db and return current state of db
def getDB():
    # Database configuration
    db = pymysql.connect(
        host=os.environ.get("DATABASE_HOST"),
        port=int(os.environ.get("DATABASE_PORT")),
        user=os.environ.get("DATABASE_USERNAME"),
        password=os.environ.get("DATABASE_PASSWORD"),
        database=os.environ.get("DATABASE"),
        cursorclass=pymysql.cursors.DictCursor
    )
    return db

# Data model
class Task(BaseModel):
    name: str
    description: str
    completed: bool
    startdate: date | None = None
    enddate: date | None = None

# response message object
class ResponseMessage(BaseModel):
    message: str

# POST
@app.post("/tasks/", response_model=Task | ResponseMessage)
async def create_task(task: Task):
    # Check if a task with the same name already exists
    db = getDB()
    with db.cursor() as cursor:
        query = "SELECT id FROM tasks WHERE name = %s"
        cursor.execute(query, (task.name))
        existing_task = cursor.fetchone()
        
        if existing_task:
            # response code when task already exists?
            return ResponseMessage(message="Task already exists with the same name")

        query = "INSERT INTO tasks (name, description, completed, startdate, enddate) VALUES (%s, %s, %s, %s, %s)"
        values = (task.name, task.description, task.completed, task.startdate, task.enddate)
        cursor.execute(query, values)
        db.commit()
        return task
 
# @app.get("/")
# async def root_route():
#     return {"root": "route"}

# GET all
@app.get("/tasks/", response_model=list[Task])
async def get_all_tasks():
    db = getDB()
    with db.cursor() as cursor:
        query = "SELECT * FROM tasks"
        cursor.execute(query)
        all_tasks = cursor.fetchall()
        return all_tasks

# GET by id
@app.get("/tasks/{task_id}", response_model=Task)
async def get_task_by_id(
    task_id: int = Path(description="id of the task to get")
):
    db = getDB()
    with db.cursor() as cursor:
        query = "SELECT * FROM tasks WHERE id = %s"
        cursor.execute(query, (task_id))
        task = cursor.fetchone()
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

# GET by name
@app.get("/tasks/by_name/", response_model=Task)
async def get_task_by_name(
    name: str = Query(description="Name of the task to get")
):
    db = getDB()
    with db.cursor() as cursor:
        query = "SELECT * FROM tasks WHERE name = %s"
        cursor.execute(query, (name,))
        task = cursor.fetchone()
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

# UPDATE by id     
@app.put("/tasks/{task_id}", response_model=Task | ResponseMessage)
async def update_task_by_id(
    *, 
    task_id: int = Path(description="id of the task to update"), 
    updated_task: Task
):
    db = getDB()
    update_values = []
    with db.cursor() as cursor:
        query = "SELECT * FROM tasks WHERE id = %s"
        cursor.execute(query, (task_id,))
        find_task = cursor.fetchone()
        if find_task is None:
            raise HTTPException(status_code=404, detail="Task not found")

        query = "SELECT id FROM tasks WHERE name = %s AND id != %s"
        cursor.execute(query, (updated_task.name, task_id))
        existing_task = cursor.fetchone()
        if existing_task:
            return ResponseMessage(message="Task already exists with the same name")

        query = "UPDATE tasks SET"
        if updated_task.name:
            query += " name = %s,"
            update_values.append(updated_task.name)
        if updated_task.description:
            query += " description = %s,"
            update_values.append(updated_task.description)
        if updated_task.completed is not None:
            query += " completed = %s,"
            update_values.append(updated_task.completed)
        if updated_task.startdate:
            query += " startdate = %s,"
            update_values.append(updated_task.startdate)
        if updated_task.enddate:
            query += " enddate = %s,"
            update_values.append(updated_task.enddate)  

        # Remove the trailing comma and complete the query
        query = query.rstrip(",") + " WHERE id = %s"
        update_values.append(task_id)

        cursor.execute(query, update_values)
        db.commit()

        # Retrieve the updated task from the database
        updated_query = "SELECT * FROM tasks WHERE id = %s"
        cursor.execute(updated_query, (task_id))
        task = cursor.fetchone()

        return task

# DELETE by id
@app.delete("/tasks/{task_id}", response_model=ResponseMessage)
async def delete_task_by_id(
    task_id: int= Path(description="id of the task to delete")
):
    db = getDB()
    with db.cursor() as cursor:
        query = "SELECT * FROM tasks WHERE id = %s"
        cursor.execute(query, (task_id))
        task = cursor.fetchone()
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")

        query = "DELETE FROM tasks WHERE id = %s"
        cursor.execute(query, (task_id))
        db.commit()
        return ResponseMessage(message="Task deleted")

# DELETE by name
# @app.delete("/tasks/delete_by_name", response_model=Task)
# async def delete_task_by_name(
#     name: str = Query(description="Name of the task to delete")
# ):
#     with db.cursor() as cursor:
#         query = "SELECT * FROM tasks WHERE name = %s"
#         cursor.execute(query, (name,))
#         task = cursor.fetchone()
#         if task is None:
#             raise HTTPException(status_code=404, detail="Task not found")

#         query = "DELETE FROM tasks WHERE name = %s"
#         cursor.execute(query, (name,))
#         db.commit()
#         return task