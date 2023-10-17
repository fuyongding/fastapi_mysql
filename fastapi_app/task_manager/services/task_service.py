from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..schemas.tasks import TaskCreate, TaskBase
from ..daos.task_dao import TaskDAO, task_dao
from ..db.models import Person, Task
from ..services.person_service import person_service
from ..rabbitmq.rabbitmq_service import RabbitMQService
from datetime import datetime


class TaskService:
    def __init__(self, task_dao_param: TaskDAO):
        self.task_dao = task_dao_param
        self.rabbitmq_service = RabbitMQService('rabbitmq3')
        self.rabbitmq_service.connect()

    def create_new_task(
        self, task: TaskCreate, person_id: int, db: Session
    ) -> Optional[Task]:
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
        db_person = person_service.get_person_by_id(db=db, person_id=person_id) # if exception not raised here, means person exists

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
        db_task: Task = self.task_dao.create_new_task(
            task=task, person_id=person_id, db=db
        )

        if not db_task:
            return None
        
        notificationMessage: str = f"TASK CREATE: {db_task.name}, PERSON ASSIGNED: {db_task.assigned_person}"
        self.rabbitmq_service.publish(message=notificationMessage)

        return db_task

    def get_all_tasks(self, db: Session) -> Optional[list[Task]]:
        return self.task_dao.get_all_tasks(db=db)

    def get_task_by_id(self, task_id: int, db: Session) -> Optional[Task]:
        db_task: Task = self.task_dao.get_task_by_id(task_id=task_id, db=db)
        if not db_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task with this id does not exist",
            )
        return db_task

    def update_task_by_id(
        self, task_id: int, task_update: TaskBase, db: Session
    ) -> Optional[Person]:
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
        
        updated_task = self.task_dao.update_task_by_id(
            task_id=task_id, task_update=task_update, db=db
        )
        if updated_task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task with this id does not exist",
            )
        
        notificationMessage: str = f"TASK UPDATED: {updated_task.name}, PERSON ASSIGNED: {updated_task.assigned_person}"
        self.rabbitmq_service.publish(message=notificationMessage)

        return updated_task
    
    def delete_task_by_id(self, task_id: int, db: Session) -> bool:
        delete_success = self.task_dao.delete_task_by_id(task_id=task_id, db=db)
        if not delete_success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )
        
        notificationMessage: str = f"TASK ID {task_id} DELETED"
        self.rabbitmq_service.publish(message=notificationMessage)

        return delete_success


task_service: TaskService = TaskService(task_dao)
