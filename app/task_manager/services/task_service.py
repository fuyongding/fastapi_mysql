from typing import Optional
from sqlalchemy.orm import Session

from ..schemas import TaskCreate, TaskBase
from ..daos.task_dao import TaskDAO, task_dao
from ..models import Person, Task


class TaskService:
    def __init__(self, task_dao_param: TaskDAO):
        self.task_dao = task_dao_param

    def create_new_task(
        self, task: TaskCreate, person_id: int, db: Session
    ) -> Optional[Task]:
        db_task: Task = self.task_dao.create_new_task(
            task=task, person_id=person_id, db=db
        )

        if not db_task:
            return None

        return db_task

    def get_all_tasks(self, db: Session) -> Optional[list[Task]]:
        return self.task_dao.get_all_tasks(db=db)

    def get_task_by_id(self, task_id: int, db: Session) -> Optional[Task]:
        db_task: Task = self.task_dao.get_task_by_id(task_id=task_id, db=db)
        return db_task

    def update_task_by_id(
        self, task_id: int, task_update: TaskBase, db: Session
    ) -> Optional[Person]:
        return self.task_dao.update_task_by_id(
            task_id=task_id, task_update=task_update, db=db
        )
    
    def delete_task_by_id(self, task_id: int, db: Session) -> bool:
        return self.task_dao.delete_task_by_id(task_id=task_id, db=db)


task_service: TaskService = TaskService(task_dao)
