from typing import Optional
from sqlalchemy.orm import Session

from ..schemas import PersonCreate, PersonBase
from ..models import Person


class PersonDAO:
    def create_new_person(self, person: PersonCreate, db: Session) -> Person:
        """create new person

        Args:
            db (Session): local db session
            person (schemas.PersonCreate): model for creating person

        Returns:
            Person: newly created person
        """
        db_person: Person = Person(**person.model_dump())

        db.add(db_person)
        db.commit()
        db.refresh(db_person)

        return db_person

    def get_person_by_name(self, name: str, db: Session) -> Person:
        """get person by name

        Args:
            db (Session): local db session
            name (str): name of person to get

        Returns:
            Person: queried person
        """
        db_person = db.query(Person).filter(Person.name == name).first()

        return db_person

    def get_all_persons(self, db: Session) -> list[Person]:
        """get all persons

        Args:
            db (Session): local db session

        Returns:
            list[Person]: list of all people
        """
        persons: list[Person] = db.query(Person).all()
        return persons

    def get_person_by_id(self, person_id: int, db: Session) -> Person:
        """get person by id

        Args:
            db (Session): local db session
            person_id (int): id of person to get

        Returns:
            Person: queried person
        """
        db_person = db.query(Person).filter(Person.id == person_id).first()
        return db_person

    def update_person_by_id(
        self, person_id: int, person_update: PersonBase, db: Session
    ) -> Optional[Person]:
        """update person by id

        Args:
            db (Session): local db session
            person_id (int): id of person to update
            person_update (schemas.PersonBase): new details of person

        Returns:
            Person: person with updated details
        """
        existing_person = db.query(Person).filter(Person.id == person_id).first()

        if existing_person is None:
            return None

        for attr, value in person_update.model_dump().items():
            setattr(existing_person, attr, value)

        db.commit()
        db.refresh(existing_person)
        return existing_person

    def delete_person_by_id(self, person_id: int, db: Session) -> bool:
        """delete person by id

        Args:
            db (Session): local db session
            person_id (int): id of person to delete

        Returns:
            boolean: True if delete success, else False
        """
        existing_person = db.query(Person).filter(Person.id == person_id).first()
        if existing_person:
            db.delete(existing_person)
            db.commit()
            return True
        return False


# instantiate person_dao object here
person_dao: PersonDAO = PersonDAO()
