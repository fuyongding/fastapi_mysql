import pytest
from fastapi.testclient import TestClient
from ..main import app
from database import database
from model import models
from datetime import datetime

client = TestClient(app)


@pytest.fixture(scope="function")
def db():
    """
    Fixture to create a new database session and create tables for before each test
    Drops table and closes session after each test
    """
    print("getting db")
    db = database.SessionLocal()
    models.Base.metadata.create_all(bind=database.engine)
    try:
        yield db
    finally:
        print("closing db")
        models.Base.metadata.drop_all(bind=database.engine)
        db.close()


@pytest.mark.parametrize(
    "valid_name",
    [
        "John Doe",
        "Alice Smith",
    ],
)
def test_create_person_valid(db, valid_name):
    """
    Test create of valid persons
    """
    response_create = client.post("/persons", json={"name": valid_name})
    assert response_create.status_code == 201
    created_person = response_create.json()
    assert created_person["name"] == valid_name


@pytest.mark.parametrize(
    "invalid_name",
    [
        "",
        "A" * 51,
    ],
)
def test_create_person_invalid_name(db, invalid_name):
    """
    Test create invalid person with invalid name
    """
    response_create = client.post("/persons", json={"name": invalid_name})
    assert response_create.status_code == 400


@pytest.mark.parametrize(
    "test_person_data",
    [
        ({"name": "Alice Smith"}),
        ({"name": "John Doe"}),
    ],
)
def test_create_person_invalid_duplicate_name(db, test_person_data):
    """
    Test create invalid person with duplicate name
    """
    test_existing_person_data = [{"name": "John Doe"}, {"name": "Alice Smith"}]

    for test_data in test_existing_person_data:
        response_create_person = client.post("/persons", json=test_data)
        assert response_create_person.status_code == 201

    response_create = client.post("/persons", json=test_person_data)
    assert response_create.status_code == 400


def test_get_all_persons(db):
    """
    Test get all persons endpoint
    """
    response = client.get("/persons/")
    assert response.status_code == 200
    persons = response.json()
    assert persons == []

    test_person_data = [{"name": "John Doe"}, {"name": "Alice Smith"}]
    for person_data in test_person_data:
        response_create_person = client.post("/persons", json=person_data)
        assert response_create_person.status_code == 201

    read_response = client.get("/persons/")
    assert read_response.status_code == 200
    all_persons = read_response.json()
    name_to_id = {person["name"]: person["id"] for person in all_persons}

    for person_data in test_person_data:
        person_name = person_data["name"]
        expected_id = name_to_id.get(person_name)
        assert expected_id == 1 if person_name == "John Doe" else expected_id == 2


def test_get_person_by_id_valid(db):
    """
    test get person by id endpoints
    """
    test_person_data = [{"name": "John Doe"}, {"name": "Alice Smith"}]
    for person_data in test_person_data:
        response_create_person = client.post("/persons", json=person_data)
        assert response_create_person.status_code == 201

    read_response_id_one = client.get("/persons/1")
    assert read_response_id_one.status_code == 200
    person_one = read_response_id_one.json()
    assert person_one["name"] == "John Doe"
    assert person_one["id"] == 1

    read_response_id_two = client.get("/persons/2")
    assert read_response_id_two.status_code == 200
    person_two = read_response_id_two.json()
    assert person_two["name"] == "Alice Smith"
    assert person_two["id"] == 2


def test_get_person_by_id_not_found(db):
    """
    test get person where id does not exist
    """
    read_response_id_not_found = client.get("/persons/69")
    assert read_response_id_not_found.status_code == 404


def test_update_person_by_id_valid(db):
    """
    test update person by id
    """
    test_person_data = {"name": "John Doe"}
    test_person_update_data = {"name": "Alice smith"}

    response_create_person = client.post("/persons", json=test_person_data)
    assert response_create_person.status_code == 201
    created_person = response_create_person.json()
    assert created_person["name"] == "John Doe"
    response_update_person = client.put(
        f'/persons/{created_person["id"]}', json=test_person_update_data
    )
    assert response_update_person.status_code == 200
    updated_person = response_update_person.json()
    assert updated_person["name"] == test_person_update_data["name"]


@pytest.mark.parametrize(
    "invalid_name",
    [
        "",
        "A" * 51,
    ],
)
def test_update_person_by_id_invalid(db, invalid_name):
    """
    test update person by id, invalid cases
    1) empty string for name
    2) length of name exceeds maximum character limit
    """
    test_person_data = {"name": "John Doe"}

    response_create_person = client.post("/persons", json=test_person_data)
    assert response_create_person.status_code == 201
    created_person = response_create_person.json()
    response_update_person = client.put(
        f'/persons/{created_person["id"]}', json={"name": invalid_name}
    )
    assert response_update_person.status_code == 400


def test_update_person_by_id_not_found(db):
    """
    test update person where id does not exist
    """
    test_person_update_data = {"name": "John Doe"}
    update_person_id_not_found_response = client.put(
        "/persons/69", json=test_person_update_data
    )
    assert update_person_id_not_found_response.status_code == 404


def test_delete_person_by_id_valid(db):
    """
    test delete person by id
    """
    test_person_data = {"name": "John Doe"}

    response_create_person = client.post("/persons", json=test_person_data)
    assert response_create_person.status_code == 201
    created_person = response_create_person.json()
    test_task_data = [
        {
            "name": "Task 1",
            "description": "Description 1",
            "completed": True,
            "startdate": "2023-09-10",
            "enddate": "2023-09-10",
        },
        {
            "name": "Task 2",
            "description": "Description 2",
            "completed": False,
            "startdate": "2023-09-08",
            "enddate": None,
        },
    ]
    for task_data in test_task_data:
        response_create_task = client.post(
            "/tasks", json=task_data, params={"person_id": created_person["id"]}
        )
        assert response_create_task.status_code == 201

    # test deletion of person, which will cascade to delete the person's tasks
    delete_person_response = client.delete("/persons/1")
    assert delete_person_response.status_code == 204
    get_task_one_response = client.get("/tasks/1")
    assert get_task_one_response.status_code == 404
    get_task_two_response = client.get("/tasks/2")
    assert get_task_two_response.status_code == 404


def test_delete_person_by_id_not_found(db):
    """
    test delete person where id does not exist
    """
    delete_person_id_not_found_response = client.delete("/persons/69")
    assert delete_person_id_not_found_response.status_code == 404


# --------------------------------------------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "task_data",
    [
        (
            {
                "name": "Task 1",
                "description": "Description 1",
                "completed": False,
                "startdate": "2023-09-07",
                "enddate": None,
            }
        ),
        (
            {
                "name": "Task 2",
                "description": "Description 2",
                "completed": True,
                "startdate": "2023-09-08",
                "enddate": "2023-09-10",
            }
        ),
    ],
)
def test_create_task_valid(db, task_data):
    """
    Test create valid tasks
    """
    test_person_data = {"name": "John Doe"}

    response_create_person = client.post("/persons", json=test_person_data)
    assert response_create_person.status_code == 201
    created_person = response_create_person.json()

    response_create_task = client.post(
        "/tasks", json=task_data, params={"person_id": created_person["id"]}
    )
    assert response_create_task.status_code == 201
    created_task = response_create_task.json()
    assert created_task["name"] == task_data["name"]
    assert created_task["description"] == task_data["description"]
    assert created_task["completed"] == task_data["completed"]
    assert created_task["startdate"] == task_data["startdate"]
    assert created_task["enddate"] == task_data["enddate"]


@pytest.mark.parametrize(
    "task_data",
    [
        (
            {
                "name": "",
                "description": "Description 1",
                "completed": False,
                "startdate": "2023-09-07",
                "enddate": None,
            }
        ),
        (
            {
                "name": "A" * 51,
                "description": "Description 2",
                "completed": True,
                "startdate": "2023-09-08",
                "enddate": "2023-09-10",
            }
        ),
        (
            {
                "name": "Task 1",
                "description": "A" * 101,
                "completed": False,
                "startdate": "2023-09-07",
                "enddate": None,
            }
        ),
        (
            {
                "name": "Task 2",
                "description": "B" * 101,
                "completed": True,
                "startdate": "2023-09-08",
                "enddate": "2023-09-10",
            }
        ),
        (
            {
                "name": "Task 1",
                "description": "Description 1",
                "completed": False,
                "startdate": None,
                "enddate": "2023-09-10",
            }
        ),
        (
            {
                "name": "Task 2",
                "description": "Description 2",
                "completed": True,
                "startdate": None,
                "enddate": None,
            }
        ),
        (
            {
                "name": "Task 1",
                "description": "Description 1",
                "completed": False,
                "startdate": "2023-09-10",
                "enddate": "2023-09-09",
            }
        ),
        (
            {
                "name": "Task 2",
                "description": "Description 2",
                "completed": True,
                "startdate": "2023-09-10",
                "enddate": "2023-09-01",
            }
        ),
        (
            {
                "name": "Task 1",
                "description": "Description 1",
                "completed": True,
                "startdate": "2023-09-05",
                "enddate": None,
            }
        ),
        (
            {
                "name": "Task 2",
                "description": "Description 2",
                "completed": False,
                "startdate": "2023-09-01",
                "enddate": "2023-09-10",
            }
        ),
    ],
)
def test_create_task_invalid_fields(db, task_data):
    """
    Test create tasks with invalid fields
    1) invalid name
        - empty name
        - length of name exceed character limit
    2) invalid description
        - length of description exceed character limit
    3) invalid start date
        - empty start date
    4) end date earlier than start date
    5) invalid completed and end date values
        - completed: True, enddate: None
        - completed: False, enddate: not None
    """
    test_person_data = {"name": "John Doe"}

    response_create_person = client.post("/persons", json=test_person_data)
    assert response_create_person.status_code == 201
    created_person = response_create_person.json()

    response_create_task = client.post(
        "/tasks", json=task_data, params={"person_id": created_person["id"]}
    )
    assert response_create_task.status_code == 400


@pytest.mark.parametrize(
    "invalid_date, expected_status_code",
    [
        ("2023-09-15T10:00:00", 422),  # Invalid format
        ("2023-09-15 10:00:00", 422),  # Invalid format
        ("15/09/2023", 422),  # Invalid format
        ("2023-09-39", 422),  # Invalid day
        ("2023-13-15", 422),  # Invalid month
    ],
)
def test_create_task_invalid_wrong_date_format(db, invalid_date, expected_status_code):
    """
    test create tasks with invalid date format
    """
    test_person_data = {"name": "John Doe"}
    response_create_person = client.post("/persons", json=test_person_data)
    assert response_create_person.status_code == 201
    created_person = response_create_person.json()

    response = client.post(
        "/tasks",
        json={
            "name": "Test Task",
            "startdate": invalid_date,
            "enddate": "2023-09-16",
        },
        params={"person_id": created_person["id"]},
    )

    assert response.status_code == expected_status_code


def test_get_all_tasks(db):
    """
    test get all tasks endpoint
    """
    response = client.get("/tasks/")
    assert response.status_code == 200
    tasks = response.json()
    assert tasks == []

    test_person_data = {"name": "John Doe"}
    response_create_person = client.post("/persons", json=test_person_data)
    assert response_create_person.status_code == 201
    created_person = response_create_person.json()

    test_task_data = [
        {
            "name": "Task 1",
            "description": "Description 1",
            "completed": True,
            "startdate": "2023-09-10",
            "enddate": "2023-09-10",
        },
        {
            "name": "Task 2",
            "description": "Description 2",
            "completed": False,
            "startdate": "2023-09-08",
            "enddate": None,
        },
    ]
    for task_data in test_task_data:
        response_create_task = client.post(
            "/tasks", json=task_data, params={"person_id": created_person["id"]}
        )
        assert response_create_task.status_code == 201

    read_response = client.get("/tasks/")
    assert read_response.status_code == 200
    all_tasks = read_response.json()
    name_to_id = {task["name"]: task["id"] for task in all_tasks}

    for task_data in test_task_data:
        task_name = task_data["name"]
        expected_id = name_to_id.get(task_name)
        assert expected_id == 1 if task_name == "Task 1" else expected_id == 2

        task = next(task for task in all_tasks if task["id"] == expected_id)
        assert task["description"] == task_data["description"]
        assert task["completed"] == task_data["completed"]
        assert task["startdate"] == task_data["startdate"]
        assert task["enddate"] == task_data["enddate"]


@pytest.mark.parametrize(
    "task_data",
    [
        (
            {
                "name": "Task 1",
                "description": "Description 1",
                "completed": True,
                "startdate": "2023-09-10",
                "enddate": "2023-09-10",
            }
        ),
        (
            {
                "name": "Task 2",
                "description": "Description 2",
                "completed": False,
                "startdate": "2023-09-08",
                "enddate": None,
            }
        ),
    ],
)
def test_get_task_by_id_valid(db, task_data):
    """
    test get task by id, valid
    """
    test_person_data = {"name": "John Doe"}

    response_create_person = client.post("/persons", json=test_person_data)
    assert response_create_person.status_code == 201
    created_person = response_create_person.json()
    response_create_task = client.post(
        "/tasks", json=task_data, params={"person_id": created_person["id"]}
    )
    assert response_create_task.status_code == 201

    read_response = client.get("/tasks/1")
    assert read_response.status_code == 200
    read_task = read_response.json()
    assert read_task["id"] == 1
    assert read_task["name"] == task_data["name"]
    assert read_task["description"] == task_data["description"]
    assert read_task["completed"] == task_data["completed"]
    assert read_task["startdate"] == task_data["startdate"]
    assert read_task["enddate"] == task_data["enddate"]


def test_get_task_by_id_not_found(db):
    """
    test get task where id does not exist
    """
    read_response_id_not_found = client.get("/tasks/69")
    assert read_response_id_not_found.status_code == 404


@pytest.mark.parametrize(
    "update_task_data",
    [
        (
            {
                "name": "Task 1",
                "description": "Description 1",
                "completed": False,
                "startdate": "2023-09-07",
                "enddate": None,
            }
        ),
        (
            {
                "name": "Task 2",
                "description": "Description 2",
                "completed": True,
                "startdate": "2023-09-08",
                "enddate": "2023-09-10",
            }
        ),
    ],
)
def test_update_task_by_id_valid(db, update_task_data):
    """
    Test update task by id, valid
    """
    test_person_data = {"name": "John Doe"}

    response_create_person = client.post("/persons", json=test_person_data)
    assert response_create_person.status_code == 201
    created_person = response_create_person.json()

    test_task_data = {
        "name": "Updated task name",
        "description": "Update description",
        "completed": True,
        "startdate": "2023-09-06",
        "enddate": "2023-09-15",
    }

    response_create_task = client.post(
        "/tasks", json=test_task_data, params={"person_id": created_person["id"]}
    )
    assert response_create_task.status_code == 201
    created_task = response_create_task.json()
    assert created_task["name"] == test_task_data["name"]
    assert created_task["description"] == test_task_data["description"]
    assert created_task["completed"] == test_task_data["completed"]
    assert created_task["startdate"] == test_task_data["startdate"]
    assert created_task["enddate"] == test_task_data["enddate"]

    response_update_task = client.put(
        f"/tasks/{created_task['id']}", json=update_task_data
    )
    assert response_update_task.status_code == 200
    updated_task = response_update_task.json()
    assert updated_task["name"] == update_task_data["name"]
    assert updated_task["description"] == update_task_data["description"]
    assert updated_task["completed"] == update_task_data["completed"]
    assert updated_task["startdate"] == update_task_data["startdate"]
    assert updated_task["enddate"] == update_task_data["enddate"]


@pytest.mark.parametrize(
    "update_task_data",
    [
        (
            {
                "name": "",
                "description": "Description 1",
                "completed": False,
                "startdate": "2023-09-07",
                "enddate": None,
            }
        ),
        (
            {
                "name": "A" * 51,
                "description": "Description 2",
                "completed": True,
                "startdate": "2023-09-08",
                "enddate": "2023-09-10",
            }
        ),
        (
            {
                "name": "Task 1",
                "description": "A" * 101,
                "completed": False,
                "startdate": "2023-09-07",
                "enddate": None,
            }
        ),
        (
            {
                "name": "Task 2",
                "description": "B" * 101,
                "completed": True,
                "startdate": "2023-09-08",
                "enddate": "2023-09-10",
            }
        ),
        (
            {
                "name": "Task 1",
                "description": "Task 1 description",
                "completed": False,
                "startdate": None,
                "enddate": None,
            }
        ),
        (
            {
                "name": "Task 2",
                "description": "Task 2 description",
                "completed": True,
                "startdate": None,
                "enddate": "2023-09-10",
            }
        ),
        (
            {
                "name": "Task 1",
                "description": "Task 1 description",
                "completed": True,
                "startdate": "2023-09-05",
                "enddate": "2023-09-01",
            }
        ),
        (
            {
                "name": "Task 2",
                "description": "Task 2 description",
                "completed": True,
                "startdate": "2023-09-10",
                "enddate": "2023-09-01",
            }
        ),
        (
            {
                "name": "Task 1",
                "description": "Description 1",
                "completed": True,
                "startdate": "2023-09-05",
                "enddate": None,
            }
        ),
        (
            {
                "name": "Task 2",
                "description": "Description 2",
                "completed": False,
                "startdate": "2023-09-01",
                "enddate": "2023-09-10",
            }
        ),
    ],
)
def test_update_task_by_id_invalid_fields(db, update_task_data):
    """
    Test update tasks with invalid fields
    1) invalid name
        - empty name
        - length of name exceed character limit
    2) invalid description
        - length of description exceed character limit
    3) invalid start date
        - empty start date
    4) end date earlier than start date
    5) invalid completed and end date values
        - completed: True, enddate: None
        - completed: False, enddate: not None
    """
    test_person_data = {"name": "John Doe"}

    response_create_person = client.post("/persons", json=test_person_data)
    assert response_create_person.status_code == 201
    created_person = response_create_person.json()

    test_task_data = {
        "name": "task 1",
        "description": "task description",
        "completed": True,
        "startdate": "2023-09-06",
        "enddate": "2023-09-15",
    }
    response_create_task = client.post(
        "/tasks", json=test_task_data, params={"person_id": created_person["id"]}
    )
    assert response_create_task.status_code == 201

    response_update_task = client.put(
        f"/tasks/{created_person['id']}", json=update_task_data
    )
    assert response_update_task.status_code == 400


@pytest.mark.parametrize(
    "invalid_date, expected_status_code",
    [
        ("2023-09-15T10:00:00", 422),  # Invalid format
        ("2023-09-15 10:00:00", 422),  # Invalid format
        ("15/09/2023", 422),  # Invalid format
        ("2023-09-39", 422),  # Invalid day
        ("2023-13-15", 422),  # Invalid month
    ],
)
def test_update_task_by_id_invalid_wrong_date_format(
    db, invalid_date, expected_status_code
):
    """
    test update task with wrong date format
    """
    test_person_data = {"name": "John Doe"}
    response_create_person = client.post("/persons", json=test_person_data)
    assert response_create_person.status_code == 201
    created_person = response_create_person.json()

    test_task_data = {
        "name": "initial task name",
        "description": "initial task description",
        "completed": True,
        "startdate": "2023-09-06",
        "enddate": "2023-09-15",
    }
    response_create_task = client.post(
        "/tasks", json=test_task_data, params={"person_id": created_person["id"]}
    )
    assert response_create_task.status_code == 201

    response_update_task = client.put(
        f"/tasks/{created_person['id']}",
        json={
            "name": "Test Task",
            "startdate": invalid_date,
            "enddate": "2023-09-16",
        },
    )
    assert response_update_task.status_code == expected_status_code


def test_update_task_by_id_not_found(db):
    """
    test update task where id does not exist
    """
    test_task_data = {
        "name": "initial task name",
        "description": "initial task description",
        "completed": True,
        "startdate": "2023-09-06",
        "enddate": "2023-09-15",
    }
    response_update_task_id_not_found = client.put("/tasks/69", json=test_task_data)
    assert response_update_task_id_not_found.status_code == 404


def test_delete_task_by_id_valid(db):
    """
    test delete task by id endpoint, valid case
    """
    test_person_data = {"name": "John Doe"}

    response_create_person = client.post("/persons", json=test_person_data)
    assert response_create_person.status_code == 201
    created_person = response_create_person.json()

    test_task_data = [
        {
            "name": "Task 1",
            "description": "Description 1",
            "completed": True,
            "startdate": "2023-09-10",
            "enddate": "2023-09-10",
        },
        {
            "name": "Task 2",
            "description": "Description 2",
            "completed": False,
            "startdate": "2023-09-08",
            "enddate": None,
        },
    ]
    created_task_ids = []

    for task_data in test_task_data:
        response_create_task = client.post(
            "/tasks", json=task_data, params={"person_id": created_person["id"]}
        )
        assert response_create_task.status_code == 201
        created_task = response_create_task.json()
        created_task_ids.append(created_task["id"])

    # before deletion
    response_get_person = client.get(f"/persons/{created_person['id']}")
    person = response_get_person.json()
    assert len(person["tasks"]) == len(test_task_data)

    # Delete each task by its ID
    for task_id in created_task_ids:
        response_delete_task = client.delete(f"/tasks/{task_id}")
        assert response_delete_task.status_code == 204

        response_get_task = client.get(f"/tasks/{task_id}")
        assert response_get_task.status_code == 404

    # after deletion
    response_get_person = client.get(f"/persons/{created_person['id']}")
    person = response_get_person.json()
    assert len(person["tasks"]) == 0


def test_delete_task_by_id_not_found(db):
    """
    test delete task where id does not exist
    """
    response_delete_task_id_not_found = client.delete("/tasks/69")
    assert response_delete_task_id_not_found.status_code == 404


# -------------------------------------------------------------------------------

# @pytest.mark.parametrize(
#     "task_data",
#     [
#         (
#             {
#                 "name": "",
#                 "description": "Description 1",
#                 "completed": False,
#                 "startdate": "2023-09-07",
#                 "enddate": None,
#             }
#         ),
#         (
#             {
#                 "name": "A" * 51,
#                 "description": "Description 2",
#                 "completed": True,
#                 "startdate": "2023-09-08",
#                 "enddate": "2023-09-10",
#             }
#         )
#     ],
# )
# def test_create_task_invalid_name(db, task_data):
#     """
#     Test create tasks with invalid name
#     1) empty string
#     2) exceed character count
#     """
#     test_person_data = {"name": "John Doe"}

#     response_create_person = client.post("/persons", json=test_person_data)
#     assert response_create_person.status_code == 201
#     created_person = response_create_person.json()

#     response_create_task = client.post(
#         "/tasks", json=task_data, params={"person_id": created_person["id"]}
#     )
#     assert response_create_task.status_code == 400


# @pytest.mark.parametrize(
#     "task_data",
#     [
#         (
#             {
#                 "name": "Task 1",
#                 "description": "A" * 101,
#                 "completed": False,
#                 "startdate": "2023-09-07",
#                 "enddate": None,
#             }
#         ),
#         (
#             {
#                 "name": "Task 2",
#                 "description": "B" * 101,
#                 "completed": True,
#                 "startdate": "2023-09-08",
#                 "enddate": "2023-09-10",
#             }
#         ),
#     ],
# )
# def test_create_task_invalid_description(db, task_data):
#     """
#     test create task with description that exceeds character limit
#     """
#     test_person_data = {"name": "John Doe"}

#     response_create_person = client.post("/persons", json=test_person_data)
#     assert response_create_person.status_code == 201
#     created_person = response_create_person.json()

#     response_create_task = client.post(
#         "/tasks", json=task_data, params={"person_id": created_person["id"]}
#     )
#     assert response_create_task.status_code == 400


# @pytest.mark.parametrize(
#     "task_data",
#     [
#         (
#             {
#                 "name": "Task 1",
#                 "description": "Description 1",
#                 "completed": False,
#                 "startdate": None,
#                 "enddate": "2023-09-10",
#             }
#         ),
#         (
#             {
#                 "name": "Task 2",
#                 "description": "Description 2",
#                 "completed": True,
#                 "startdate": None,
#                 "enddate": None,
#             }
#         ),
#     ],
# )
# def test_create_task_invalid_empty_start_date(db, task_data):
#     """
#     test create task with null start date
#     """
#     test_person_data = {"name": "John Doe"}

#     response_create_person = client.post("/persons", json=test_person_data)
#     assert response_create_person.status_code == 201
#     created_person = response_create_person.json()

#     response_create_task = client.post(
#         "/tasks", json=task_data, params={"person_id": created_person["id"]}
#     )
#     assert response_create_task.status_code == 400


# @pytest.mark.parametrize(
#     "task_data",
#     [
#         (
#             {
#                 "name": "Task 1",
#                 "description": "Description 1",
#                 "completed": False,
#                 "startdate": "2023-09-10",
#                 "enddate": "2023-09-09",
#             }
#         ),
#         (
#             {
#                 "name": "Task 2",
#                 "description": "Description 2",
#                 "completed": True,
#                 "startdate": "2023-09-10",
#                 "enddate": "2023-09-01",
#             }
#         ),
#     ],
# )
# def test_create_task_invalid_end_date_earlier_than_start_date(db, task_data):
#     """
#     test create task with end date earlier than start date
#     """
#     test_person_data = {"name": "John Doe"}

#     response_create_person = client.post("/persons", json=test_person_data)
#     assert response_create_person.status_code == 201
#     created_person = response_create_person.json()

#     response_create_task = client.post(
#         "/tasks", json=task_data, params={"person_id": created_person["id"]}
#     )
#     assert response_create_task.status_code == 400
#
# @pytest.mark.parametrize(
#     "task_data",
#     [
#         (
#             {
#                 "name": "Task 1",
#                 "description": "Description 1",
#                 "completed": True,
#                 "startdate": "2023-09-05",
#                 "enddate": None,
#             }
#         ),
#         (
#             {
#                 "name": "Task 2",
#                 "description": "Description 2",
#                 "completed": False,
#                 "startdate": "2023-09-01",
#                 "enddate": "2023-09-10",
#             }
#         ),
#     ],
# )
# def test_create_task_invalid_completed_and_end_date_values(db, task_data):
#     """
#     test create tasks with invalid completed and enddate values
#     1) completed: True, enddate: null
#     2) completed: False, enddate: exists
#     """
#     test_person_data = {"name": "John Doe"}

#     response_create_person = client.post("/persons", json=test_person_data)
#     assert response_create_person.status_code == 201
#     created_person = response_create_person.json()

#     response_create_task = client.post(
#         "/tasks", json=task_data, params={"person_id": created_person["id"]}
#     )
#     assert response_create_task.status_code == 400

# @pytest.mark.parametrize(
#     "update_task_data",
#     [
#         (
#             {
#                 "name": "",
#                 "description": "Description 1",
#                 "completed": False,
#                 "startdate": "2023-09-07",
#                 "enddate": None,
#             }
#         ),
#         (
#             {
#                 "name": "A" * 51,
#                 "description": "Description 2",
#                 "completed": True,
#                 "startdate": "2023-09-08",
#                 "enddate": "2023-09-10",
#             }
#         ),
#     ],
# )
# def test_update_task_by_id_invalid_name(db, update_task_data):
#     """
#     Test update tasks with invalid name
#     1) empty string
#     2) exceed character count
#     """
#     test_person_data = {"name": "John Doe"}

#     response_create_person = client.post("/persons", json=test_person_data)
#     assert response_create_person.status_code == 201
#     created_person = response_create_person.json()

#     test_task_data = {
#         "name": "task 1",
#         "description": "task description",
#         "completed": True,
#         "startdate": "2023-09-06",
#         "enddate": "2023-09-15",
#     }
#     response_create_task = client.post(
#         "/tasks", json=test_task_data, params={"person_id": created_person["id"]}
#     )
#     assert response_create_task.status_code == 201

#     response_update_task = client.put(
#         f"/tasks/{created_person['id']}", json=update_task_data
#     )
#     assert response_update_task.status_code == 400


# @pytest.mark.parametrize(
#     "update_task_data",
#     [
#         (
#             {
#                 "name": "Task 1",
#                 "description": "A" * 101,
#                 "completed": False,
#                 "startdate": "2023-09-07",
#                 "enddate": None,
#             }
#         ),
#         (
#             {
#                 "name": "Task 2",
#                 "description": "B" * 101,
#                 "completed": True,
#                 "startdate": "2023-09-08",
#                 "enddate": "2023-09-10",
#             }
#         ),
#     ],
# )
# def test_update_task_by_id_invalid_description(db, update_task_data):
#     """
#     test update task with description that exceeds character limit
#     """
#     test_person_data = {"name": "John Doe"}

#     response_create_person = client.post("/persons", json=test_person_data)
#     assert response_create_person.status_code == 201
#     created_person = response_create_person.json()

#     test_task_data = {
#         "name": "task 1",
#         "description": "task description",
#         "completed": True,
#         "startdate": "2023-09-06",
#         "enddate": "2023-09-15",
#     }
#     response_create_task = client.post(
#         "/tasks", json=test_task_data, params={"person_id": created_person["id"]}
#     )
#     assert response_create_task.status_code == 201

#     response_update_task = client.put(
#         f"/tasks/{created_person['id']}", json=update_task_data
#     )
#     assert response_update_task.status_code == 400


# @pytest.mark.parametrize(
#     "update_task_data",
#     [
#         (
#             {
#                 "name": "Task 1",
#                 "description": "Task 1 description",
#                 "completed": False,
#                 "startdate": None,
#                 "enddate": None,
#             }
#         ),
#         (
#             {
#                 "name": "Task 2",
#                 "description": "Task 2 description",
#                 "completed": True,
#                 "startdate": None,
#                 "enddate": "2023-09-10",
#             }
#         ),
#     ],
# )
# def test_update_task_by_id_invalid_empty_start_date(db, update_task_data):
#     """
#     test update task with empty start date
#     """
#     test_person_data = {"name": "John Doe"}

#     response_create_person = client.post("/persons", json=test_person_data)
#     assert response_create_person.status_code == 201
#     created_person = response_create_person.json()

#     test_task_data = {
#         "name": "initial task name",
#         "description": "initial task description",
#         "completed": True,
#         "startdate": "2023-09-06",
#         "enddate": "2023-09-15",
#     }
#     response_create_task = client.post(
#         "/tasks", json=test_task_data, params={"person_id": created_person["id"]}
#     )
#     assert response_create_task.status_code == 201

#     response_update_task = client.put(
#         f"/tasks/{created_person['id']}", json=update_task_data
#     )
#     assert response_update_task.status_code == 400


# @pytest.mark.parametrize(
#     "update_task_data",
#     [
#         (
#             {
#                 "name": "Task 1",
#                 "description": "Task 1 description",
#                 "completed": True,
#                 "startdate": "2023-09-05",
#                 "enddate": "2023-09-01",
#             }
#         ),
#         (
#             {
#                 "name": "Task 2",
#                 "description": "Task 2 description",
#                 "completed": True,
#                 "startdate": "2023-09-10",
#                 "enddate": "2023-09-01",
#             }
#         ),
#     ],
# )
# def test_update_task_by_id_invalid_end_date_earlier_than_start_date(
#     db, update_task_data
# ):
#     """
#     test update task with end date earlier than start date
#     """
#     test_person_data = {"name": "John Doe"}

#     response_create_person = client.post("/persons", json=test_person_data)
#     assert response_create_person.status_code == 201
#     created_person = response_create_person.json()

#     test_task_data = {
#         "name": "initial task name",
#         "description": "initial task description",
#         "completed": True,
#         "startdate": "2023-09-06",
#         "enddate": "2023-09-15",
#     }
#     response_create_task = client.post(
#         "/tasks", json=test_task_data, params={"person_id": created_person["id"]}
#     )
#     assert response_create_task.status_code == 201

#     response_update_task = client.put(
#         f"/tasks/{created_person['id']}", json=update_task_data
#     )
#     assert response_update_task.status_code == 400
# @pytest.mark.parametrize(
#     "update_task_data",
#     [
#         (
#             {
#                 "name": "Task 1",
#                 "description": "Description 1",
#                 "completed": True,
#                 "startdate": "2023-09-05",
#                 "enddate": None,
#             }
#         ),
#         (
#             {
#                 "name": "Task 2",
#                 "description": "Description 2",
#                 "completed": False,
#                 "startdate": "2023-09-01",
#                 "enddate": "2023-09-10",
#             }
#         ),
#     ],
# )
# def test_update_tasks_by_id_invalid_completed_and_end_date_values(db, update_task_data):
#     """
#     test create tasks with invalid completed and enddate values
#     1) completed: True, enddate: null
#     2) completed: False, enddate: exists
#     """
#     test_person_data = {"name": "John Doe"}

#     response_create_person = client.post("/persons", json=test_person_data)
#     assert response_create_person.status_code == 201
#     created_person = response_create_person.json()

#     test_task_data = {
#         "name": "initial task name",
#         "description": "initial task description",
#         "completed": True,
#         "startdate": "2023-09-06",
#         "enddate": "2023-09-15",
#     }
#     response_create_task = client.post(
#         "/tasks", json=test_task_data, params={"person_id": created_person["id"]}
#     )
#     assert response_create_task.status_code == 201

#     response_update_task = client.put(
#         f"/tasks/{created_person['id']}", json=update_task_data
#     )
#     assert response_update_task.status_code == 400
