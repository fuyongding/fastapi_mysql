import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..main import app
from database import database
from model import models
from datetime import date

client = TestClient(app)

# Fixture to create and set up the database tables before the tests
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    models.Base.metadata.create_all(bind=database.engine)
    yield
    models.Base.metadata.drop_all(bind=database.engine)

# Fixture to create a new database session for each test
@pytest.fixture(scope="function")
def db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()

# PERSON TESTS
@pytest.mark.parametrize("valid_name", [
    "heibui", 
    "Alice",
])
def test_create_valid_person(db, valid_name):
    response_create = client.post("/persons", json={"name": valid_name})
    assert response_create.status_code == 200
    created_person = response_create.json()
    assert created_person["name"] == valid_name

@pytest.mark.parametrize("invalid_name", [
    "",  # Empty string
    "A" * 51,  # Exceeds the maximum character limit
])
def test_create_person_invalid_name(db, invalid_name):
    response_create = client.post("/persons", json={"name": invalid_name})
    assert response_create.status_code == 400  # Expecting a validation error

# Parameterized test cases for creating persons with duplicate names
@pytest.mark.parametrize("person_data, expected_status_code", [
    ({"name": "John Doe"}, 200),  # Valid name
    ({"name": "Alice Smith"}, 200),  # Valid name
    ({"name": "John Doe"}, 400),  # Duplicate name, expecting a 400 Bad Request
])
def test_create_person_duplicate_name(db, person_data, expected_status_code):
    response_create = client.post("/persons", json=person_data)
    assert response_create.status_code == expected_status_code




# TASK TESTS
# Additional parameterized test cases for creating valid tasks
@pytest.mark.parametrize("task_data", [
    ({"name": "Task 1", "description": "Description 1", "completed": False, "startdate": "2023-09-07", "enddate": None}),
    ({"name": "Task 2", "description": "Description 2", "completed": True, "startdate": "2023-09-08", "enddate": "2023-09-10"}),
])
def test_create_valid_task(db, task_data):
    test_person_data = {
        "name": "John Doe"
    }

    # Create a test person
    response_create_person = client.post("/persons", json=test_person_data)
    assert response_create_person.status_code == 200
    created_person = response_create_person.json()

    # Attempt to create a valid task
    response_create_task = client.post("/tasks", json=task_data, params={"person_id": created_person["id"]})
    assert response_create_task.status_code == 200  # Expecting a successful response
    created_task = response_create_task.json()
    assert created_task["name"] == task_data["name"]

# Parameterized test cases for creating tasks with invalid names
@pytest.mark.parametrize("invalid_name", [
    "",  # Empty string
    "A" * 51,  # Exceeds the maximum character limit
])
def test_create_task_invalid_name(db, invalid_name):
    test_person_data = {
        "name": "John Doe"
    }

    # Create a test person
    response_create_person = client.post("/persons", json=test_person_data)
    assert response_create_person.status_code == 200
    created_person = response_create_person.json()

    test_task_data = {
        "name": invalid_name,
        "description": "Test task",
        "completed": False,
        "startdate": "2023-09-07",
        "enddate": None
    }

    # Attempt to create a task with an invalid name
    response_create_task = client.post("/tasks", json=test_task_data, params={"person_id": created_person["id"]})
    assert response_create_task.status_code == 422

# Additional parameterized test cases for creating tasks with invalid descriptions
@pytest.mark.parametrize("task_data, expected_status_code", [
    ({"name": "Task 1", "description": "A" * 61, "completed": False, "startdate": "2023-09-07", "enddate": None}, 422),  # Exceeds the maximum character limit
    ({"name": "Task 2", "description": "B" * 61, "completed": True, "startdate": "2023-09-08", "enddate": "2023-09-10"}, 422),  # Exceeds the maximum character limit
])
def test_create_task_invalid_description(db, task_data, expected_status_code):
    test_person_data = {
        "name": "John Doe"
    }

    # Create a test person
    response_create_person = client.post("/persons", json=test_person_data)
    assert response_create_person.status_code == 200
    created_person = response_create_person.json()

    # Attempt to create a task with an invalid description
    response_create_task = client.post("/tasks", json=task_data, params={"person_id": created_person["id"]})
    assert response_create_task.status_code == expected_status_code  # Expecting a validation error

# Additional parameterized test cases for creating tasks with empty start date
@pytest.mark.parametrize("task_data, expected_status_code", [
    ({"name": "Task 1", "description": "Description 1", "completed": False, "startdate": None, "enddate": "2023-09-10"}, 422),  # Empty start date
    ({"name": "Task 2", "description": "Description 2", "completed": True, "startdate": None, "enddate": None}, 422),  # Empty start date and end date
])
def test_create_task_empty_start_date(db, task_data, expected_status_code):
    test_person_data = {
        "name": "John Doe"
    }

    # Create a test person
    response_create_person = client.post("/persons", json=test_person_data)
    assert response_create_person.status_code == 200
    created_person = response_create_person.json()

    # Attempt to create a task with an empty start date
    response_create_task = client.post("/tasks", json=task_data, params={"person_id": created_person["id"]})
    assert response_create_task.status_code == expected_status_code  # Expecting a validation error

# Additional parameterized test cases for creating tasks with end date earlier than start date
@pytest.mark.parametrize("task_data, expected_status_code", [
    ({"name": "Task 1", "description": "Description 1", "completed": False, "startdate": "2023-09-10", "enddate": "2023-09-09"}, 422),  # End date earlier than start date
    ({"name": "Task 2", "description": "Description 2", "completed": True, "startdate": "2023-09-10", "enddate": "2023-09-10"}, 422),  # End date same as start date
])
def test_create_task_end_date_earlier_than_start_date(db, task_data, expected_status_code):
    test_person_data = {
        "name": "John Doe"
    }

    # Create a test person
    response_create_person = client.post("/persons", json=test_person_data)
    assert response_create_person.status_code == 200
    created_person = response_create_person.json()

    # Attempt to create a task with an end date earlier than start date
    response_create_task = client.post("/tasks", json=task_data, params={"person_id": created_person["id"]})
    assert response_create_task.status_code == expected_status_code  # Expecting a validation error