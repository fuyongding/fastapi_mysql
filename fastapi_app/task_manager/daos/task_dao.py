from typing import Optional
from sqlalchemy.orm import Session

from ..schemas.tasks import TaskCreate, TaskBase
from ..db.models import Person, Task


class TaskDAO:
    def create_new_task(self, task: TaskCreate, person_id: int, db: Session) -> Task:
        """create new task

        Args:
            db (Session): local db session
            task (schemas.TaskCreate): task to create
            person_id (int): id of assigned person

        Returns:
            Task: newly created task
        """
        db_task = Task(**task.model_dump(), assigned_person_id=person_id)
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task

    def get_all_tasks(self, db: Session) -> list[Task]:
        """get all tasks

        Args:
            db (Session): local db session

        Returns:
            list[Task]: list of all tasks
        """
        tasks: list[Task] = db.query(Task).all()
        return tasks

    def get_task_by_id(self, task_id: int, db: Session) -> Task:
        """get task by id

        Args:
            db (Session): local db session
            task_id (int): id of task to get

        Returns:
            Task: queried task
        """
        db_task = db.query(Task).filter(Task.id == task_id).first()
        return db_task

    def update_task_by_id(
        self, task_id: int, task_update: TaskBase, db: Session
    ) -> Optional[Person]:
        """update task based on task id

        Args:
            db (Session): local db session
            task_id (int):
            task_update (schemas.PersonBase): new task

        Returns:
            Task: task with updated details
        """
        existing_task = db.query(Task).filter(Task.id == task_id).first()

        if existing_task is None:
            return None

        for attr, value in task_update.model_dump().items():
            setattr(existing_task, attr, value)

        db.commit()
        db.refresh(existing_task)
        return existing_task

    def delete_task_by_id(self, task_id: int, db: Session) -> bool:
        """delete task by id

        Args:
            db (Session): local db session
            task_id (int): id of task to delete

        Returns:
            Boolean: True if task deleted successfully, else false
        """
        existing_task = db.query(Task).filter(Task.id == task_id).first()
        if existing_task:
            db.delete(existing_task)
            db.commit()
            return True
        return False


# instantiate person_dao object here
task_dao: TaskDAO = TaskDAO()
