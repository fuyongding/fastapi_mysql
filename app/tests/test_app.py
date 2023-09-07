import pytest
from fastapi.testclient import TestClient
from ..main import app

client = TestClient(app)

# Sample data for testing
sample_person_data = {
    "name": "John Doe"
}

sample_task_data = {
    "name": "Task 1",
    "description": "Description for Task 1",
    "completed": False,
    "startdate": "2023-09-01",
    "enddate": "2023-09-07"
}

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {'hello': 'world'}

# def test_create_person():
#     response = client.post("/persons", json=sample_person_data)
#     assert response.status_code == 200
#     assert "id" in response.json()  # Ensure the response contains an "id" field