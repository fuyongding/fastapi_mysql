import pytest
from fastapi.testclient import TestClient
from ..main import app
from database import SessionLocal, engine
from datetime import date

client = TestClient(app)

@pytest.fixture(scope="function")
def db():
    """
    Fixture to create a new database session for each test
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Fixture to create and drop database tables
@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown_database():
    # Create tables
    engine.execute("CREATE DATABASE IF NOT EXISTS test_database;")
    engine.execute("USE test_database;")
    from model import models
    models.Base.metadata.create_all(bind=engine)

    # Run tests
    yield

    # Drop tables
    models.Base.metadata.drop_all(bind=engine)
    engine.execute("DROP DATABASE IF EXISTS test_database;")

# Parameterized test cases for creating persons with invalid names
@pytest.mark.parametrize("invalid_name", [
    "",  # Empty string
    "A" * 51,  # Exceeds the maximum character limit
])
def test_create_person_invalid_name(db, invalid_name):
    response_create = client.post("/persons", json={"name": invalid_name})
    assert response_create.status_code == 422  # Expecting a validation error

# Parameterized test cases for creating persons with duplicate names
@pytest.mark.parametrize("person_data, expected_status_code", [
    ({"name": "John Doe"}, 200),  # Valid name
    ({"name": "Alice Smith"}, 200),  # Valid name
    ({"name": "John Doe"}, 400),  # Duplicate name, expecting a 400 Bad Request
])
def test_create_person_duplicate_name(db, person_data, expected_status_code):
    response_create = client.post("/persons", json=person_data)
    assert response_create.status_code == expected_status_code

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





























# sample_person_data = {
#     "name": "John Doe"
# }

# sample_task_data = {
#     "name": "Task 1",
#     "description": "Description for Task 1",
#     "completed": False,
#     "startdate": "2023-09-01",
#     "enddate": "2023-09-07"
# }

# def test_read_root():
#     response = client.get("/")
#     assert response.status_code == 200
#     assert response.json() == {'hello': 'world'}

# def test_create_person():
#     response = client.post("/persons", json=sample_person_data)
#     assert response.status_code == 200
#     assert "id" in response.json()  # Ensure the response contains an "id" field