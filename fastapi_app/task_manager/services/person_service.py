from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..schemas.persons import PersonCreate, PersonBase
from ..daos.person_dao import PersonDAO, person_dao
from ..db.models import Person


class PersonService:
    def __init__(self):
        # instantiate here or instanstiate at other file
        # self.person_dao = person_dao_param
        self.person_dao = PersonDAO()

    def create_new_person(self, person: PersonCreate, db: Session) -> Optional[Person]:
        if not person.name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Person name cannot be empty!",
            )
        if len(person.name) > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Person name is too long!",
            )
        
        existing_person = self.get_person_by_name(name=person.name, db=db)
        if existing_person:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Person with this name already registered",
            )

        db_person: Person = self.person_dao.create_new_person(person=person, db=db)

        if not db_person:
            return None

        return db_person

    def get_person_by_name(self, name: str, db: Session) -> Optional[Person]:
        db_person: Person = self.person_dao.get_person_by_name(name=name, db=db)

        if not db_person:
            return None

        return db_person

    def get_all_persons(self, db: Session) -> Optional[list[Person]]:
        return self.person_dao.get_all_persons(db=db)

    def get_person_by_id(self, person_id: int, db: Session) -> Optional[Person]:
        db_person: Person = self.person_dao.get_person_by_id(person_id=person_id, db=db)
        if not db_person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Person with this id does not exist",
            )
        return db_person

    def update_person_by_id(
        self, person_id: int, person_update: PersonBase, db: Session
    ) -> Optional[Person]:
        if not person_update.name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Person name cannot be empty!",
            )
        if len(person_update.name) > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Person name is too long!",
            )

        updated_person = self.person_dao.update_person_by_id(
            person_id=person_id, person_update=person_update, db=db
        )

        if updated_person is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Person with this id does not exist",
            )
        return updated_person

    def delete_person_by_id(self, person_id: int, db: Session) -> bool:
        delete_success = self.person_dao.delete_person_by_id(person_id=person_id, db=db)
        if not delete_success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Person not found"
            )
        return delete_success


# instantiate person_service object here
person_service: PersonService = PersonService()
