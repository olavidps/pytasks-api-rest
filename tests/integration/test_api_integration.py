"""Integration tests for API endpoints with database."""

from datetime import datetime, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient


class TestAPIIntegration:
    """Integration tests for complete API workflows."""

    def test_complete_user_workflow(self, client: TestClient):
        """Test complete user lifecycle: create, read, update, delete."""
        # Create user
        user_data = {
            "email": "integration@example.com",
            "username": "integrationuser",
            "full_name": "Integration User",
        }

        create_response = client.post("/api/v1/users", json=user_data)
        assert create_response.status_code == 201
        created_user = create_response.json()
        user_id = created_user["id"]

        # Read user
        get_response = client.get(f"/api/v1/users/{user_id}")
        assert get_response.status_code == 200
        retrieved_user = get_response.json()
        assert retrieved_user["email"] == user_data["email"]
        assert retrieved_user["username"] == user_data["username"]

        # Update user
        update_data = {"full_name": "Updated Integration User"}
        update_response = client.patch(f"/api/v1/users/{user_id}", json=update_data)
        assert update_response.status_code == 200
        updated_user = update_response.json()
        assert updated_user["full_name"] == update_data["full_name"]

        # List users (should include our user)
        list_response = client.get("/api/v1/users")
        assert list_response.status_code == 200
        users_list = list_response.json()
        assert any(user["id"] == user_id for user in users_list["items"])

        # Delete user
        delete_response = client.delete(f"/api/v1/users/{user_id}")
        assert delete_response.status_code == 204

        # Verify user is deleted
        get_deleted_response = client.get(f"/api/v1/users/{user_id}")
        assert get_deleted_response.status_code == 404

    def test_complete_task_list_workflow(self, client: TestClient, test_factory):
        """Test complete task list lifecycle with owner relationship."""
        # Create owner user
        owner = test_factory.create_user()

        # Create task list
        task_list_data = {
            "name": "Integration Task List",
            "description": "A task list for integration testing",
            "owner_id": str(owner.id),
        }

        create_response = client.post("/api/v1/task-lists", json=task_list_data)
        assert create_response.status_code == 201
        created_task_list = create_response.json()
        task_list_id = created_task_list["id"]

        # Read task list
        get_response = client.get(f"/api/v1/task-lists/{task_list_id}")
        assert get_response.status_code == 200
        retrieved_task_list = get_response.json()
        assert retrieved_task_list["name"] == task_list_data["name"]
        assert retrieved_task_list["owner_id"] == str(owner.id)

        # Update task list
        update_data = {"name": "Updated Integration Task List"}
        update_response = client.patch(
            f"/api/v1/task-lists/{task_list_id}", json=update_data
        )
        assert update_response.status_code == 200
        updated_task_list = update_response.json()
        assert updated_task_list["name"] == update_data["name"]

        # List task lists filtered by owner
        list_response = client.get(f"/api/v1/task-lists?owner_id={owner.id}")
        assert list_response.status_code == 200
        task_lists = list_response.json()
        assert any(tl["id"] == task_list_id for tl in task_lists["items"])

        # Delete task list
        delete_response = client.delete(f"/api/v1/task-lists/{task_list_id}")
        assert delete_response.status_code == 204

        # Verify task list is deleted
        get_deleted_response = client.get(f"/api/v1/task-lists/{task_list_id}")
        assert get_deleted_response.status_code == 404

    def test_complete_task_workflow(self, client: TestClient, test_factory):
        """Test complete task lifecycle with relationships."""
        # Create owner and assignee users
        owner = test_factory.create_user()
        assignee = test_factory.create_user()

        # Create task list
        task_list = test_factory.create_task_list(owner)

        # Create task
        due_date = (datetime.now() + timedelta(days=7)).isoformat()
        task_data = {
            "title": "Integration Task",
            "description": "A task for integration testing",
            "status": "pending",
            "priority": "high",
            "task_list_id": str(task_list.id),
            "assigned_to_id": str(assignee.id),
            "due_date": due_date,
        }

        create_response = client.post("/api/v1/tasks", json=task_data)
        assert create_response.status_code == 201
        created_task = create_response.json()
        task_id = created_task["id"]

        # Read task
        get_response = client.get(f"/api/v1/tasks/{task_id}")
        assert get_response.status_code == 200
        retrieved_task = get_response.json()
        assert retrieved_task["title"] == task_data["title"]
        assert retrieved_task["task_list_id"] == str(task_list.id)
        assert retrieved_task["assigned_to_id"] == str(assignee.id)

        # Update task status
        update_data = {"status": "in_progress"}
        update_response = client.patch(f"/api/v1/tasks/{task_id}", json=update_data)
        assert update_response.status_code == 200
        updated_task = update_response.json()
        assert updated_task["status"] == update_data["status"]

        # List tasks with various filters
        list_response = client.get(f"/api/v1/tasks?task_list_id={task_list.id}")
        assert list_response.status_code == 200
        tasks = list_response.json()
        assert any(task["id"] == task_id for task in tasks["items"])

        # Filter by assignee
        assignee_response = client.get(f"/api/v1/tasks?assigned_to_id={assignee.id}")
        assert assignee_response.status_code == 200
        assignee_tasks = assignee_response.json()
        assert any(task["id"] == task_id for task in assignee_tasks["items"])

        # Filter by status
        status_response = client.get("/api/v1/tasks?status=in_progress")
        assert status_response.status_code == 200
        status_tasks = status_response.json()
        assert any(task["id"] == task_id for task in status_tasks["items"])

        # Delete task
        delete_response = client.delete(f"/api/v1/tasks/{task_id}")
        assert delete_response.status_code == 204

        # Verify task is deleted
        get_deleted_response = client.get(f"/api/v1/tasks/{task_id}")
        assert get_deleted_response.status_code == 404

    def test_cross_entity_relationships(self, client: TestClient, test_factory):
        """Test relationships between users, task lists, and tasks."""
        # Create multiple users
        owner = test_factory.create_user()
        assignee1 = test_factory.create_user()
        assignee2 = test_factory.create_user()

        # Create multiple task lists for the owner
        task_list1 = test_factory.create_task_list(owner, name="Personal Tasks")
        task_list2 = test_factory.create_task_list(owner, name="Work Tasks")

        # Create tasks in different lists with different assignees
        task1_data = {
            "title": "Personal Task 1",
            "task_list_id": str(task_list1.id),
            "assigned_to_id": str(assignee1.id),
            "priority": "high",
        }
        task1_response = client.post("/api/v1/tasks", json=task1_data)
        assert task1_response.status_code == 201
        task1_response.json()

        task2_data = {
            "title": "Work Task 1",
            "task_list_id": str(task_list2.id),
            "assigned_to_id": str(assignee2.id),
            "priority": "medium",
        }
        task2_response = client.post("/api/v1/tasks", json=task2_data)
        assert task2_response.status_code == 201
        task2_response.json()

        task3_data = {
            "title": "Personal Task 2",
            "task_list_id": str(task_list1.id),
            "assigned_to_id": str(assignee1.id),
            "priority": "low",
        }
        task3_response = client.post("/api/v1/tasks", json=task3_data)
        assert task3_response.status_code == 201
        task3_response.json()

        # Test filtering tasks by task list
        personal_tasks_response = client.get(
            f"/api/v1/tasks?task_list_id={task_list1.id}"
        )
        assert personal_tasks_response.status_code == 200
        personal_tasks = personal_tasks_response.json()
        assert len(personal_tasks["items"]) == 2

        work_tasks_response = client.get(f"/api/v1/tasks?task_list_id={task_list2.id}")
        assert work_tasks_response.status_code == 200
        work_tasks = work_tasks_response.json()
        assert len(work_tasks["items"]) == 1

        # Test filtering tasks by assignee
        assignee1_tasks_response = client.get(
            f"/api/v1/tasks?assigned_to_id={assignee1.id}"
        )
        assert assignee1_tasks_response.status_code == 200
        assignee1_tasks = assignee1_tasks_response.json()
        assert len(assignee1_tasks["items"]) == 2

        assignee2_tasks_response = client.get(
            f"/api/v1/tasks?assigned_to_id={assignee2.id}"
        )
        assert assignee2_tasks_response.status_code == 200
        assignee2_tasks = assignee2_tasks_response.json()
        assert len(assignee2_tasks["items"]) == 1

        # Test filtering task lists by owner
        owner_task_lists_response = client.get(
            f"/api/v1/task-lists?owner_id={owner.id}"
        )
        assert owner_task_lists_response.status_code == 200
        owner_task_lists = owner_task_lists_response.json()
        assert len(owner_task_lists["items"]) == 2

        # Test combined filters
        high_priority_personal_response = client.get(
            f"/api/v1/tasks?task_list_id={task_list1.id}&priority=high"
        )
        assert high_priority_personal_response.status_code == 200
        high_priority_personal = high_priority_personal_response.json()
        assert len(high_priority_personal["items"]) == 1
        assert high_priority_personal["items"][0]["title"] == "Personal Task 1"

    def test_pagination_across_endpoints(self, client: TestClient, test_factory):
        """Test pagination functionality across all endpoints."""
        # Create test data
        users = [test_factory.create_user() for _ in range(15)]
        owner = users[0]
        task_lists = [test_factory.create_task_list(owner) for _ in range(12)]

        # Create tasks across different task lists
        tasks = []
        for i, task_list in enumerate(task_lists[:8]):
            for j in range(3):
                task = test_factory.create_task(task_list, title=f"Task {i}-{j}")
                tasks.append(task)

        # Test user pagination
        users_page1 = client.get("/api/v1/users?page=1&size=5")
        assert users_page1.status_code == 200
        users_data1 = users_page1.json()
        assert len(users_data1["items"]) == 5
        assert users_data1["page"] == 1
        assert users_data1["size"] == 5
        assert users_data1["total"] >= 15

        users_page2 = client.get("/api/v1/users?page=2&size=5")
        assert users_page2.status_code == 200
        users_data2 = users_page2.json()
        assert len(users_data2["items"]) == 5
        assert users_data2["page"] == 2

        # Ensure different items on different pages
        page1_ids = {user["id"] for user in users_data1["items"]}
        page2_ids = {user["id"] for user in users_data2["items"]}
        assert page1_ids.isdisjoint(page2_ids)

        # Test task list pagination
        task_lists_page1 = client.get("/api/v1/task-lists?page=1&size=4")
        assert task_lists_page1.status_code == 200
        task_lists_data1 = task_lists_page1.json()
        assert len(task_lists_data1["items"]) == 4
        assert task_lists_data1["total"] >= 12

        # Test task pagination
        tasks_page1 = client.get("/api/v1/tasks?page=1&size=10")
        assert tasks_page1.status_code == 200
        tasks_data1 = tasks_page1.json()
        assert len(tasks_data1["items"]) == 10
        assert tasks_data1["total"] >= 24

        tasks_page2 = client.get("/api/v1/tasks?page=2&size=10")
        assert tasks_page2.status_code == 200
        tasks_data2 = tasks_page2.json()
        assert len(tasks_data2["items"]) >= 10

        # Test pagination with filters
        filtered_tasks = client.get(
            f"/api/v1/tasks?task_list_id={task_lists[0].id}&page=1&size=2"
        )
        assert filtered_tasks.status_code == 200
        filtered_data = filtered_tasks.json()
        assert len(filtered_data["items"]) == 2
        assert filtered_data["total"] == 3  # 3 tasks per task list

    def test_error_handling_integration(self, client: TestClient, test_factory):
        """Test error handling across the API integration."""
        # Test cascading errors (e.g., deleting user with task lists)
        owner = test_factory.create_user()
        task_list = test_factory.create_task_list(owner)
        task = test_factory.create_task(task_list)

        # Try to create task with non-existent task list
        invalid_task_data = {"title": "Invalid Task", "task_list_id": str(uuid4())}
        invalid_response = client.post("/api/v1/tasks", json=invalid_task_data)
        assert invalid_response.status_code == 400

        # Try to create task list with non-existent owner
        invalid_task_list_data = {"name": "Invalid Task List", "owner_id": str(uuid4())}
        invalid_tl_response = client.post(
            "/api/v1/task-lists", json=invalid_task_list_data
        )
        assert invalid_tl_response.status_code == 400

        # Try to assign task to non-existent user
        update_task_data = {"assigned_to_id": str(uuid4())}
        invalid_assign_response = client.patch(
            f"/api/v1/tasks/{task.id}", json=update_task_data
        )
        assert invalid_assign_response.status_code == 400

        # Test validation errors
        invalid_user_data = {
            "email": "invalid-email",
            "username": "user",
            "full_name": "User",
        }
        validation_response = client.post("/api/v1/users", json=invalid_user_data)
        assert validation_response.status_code == 422

        # Test not found errors
        not_found_response = client.get(f"/api/v1/users/{uuid4()}")
        assert not_found_response.status_code == 404

        not_found_tl_response = client.get(f"/api/v1/task-lists/{uuid4()}")
        assert not_found_tl_response.status_code == 404

        not_found_task_response = client.get(f"/api/v1/tasks/{uuid4()}")
        assert not_found_task_response.status_code == 404

    def test_data_consistency_integration(self, client: TestClient, test_factory):
        """Test data consistency across operations."""
        # Create initial data
        owner = test_factory.create_user()
        assignee = test_factory.create_user()
        task_list = test_factory.create_task_list(owner)

        # Create task
        task_data = {
            "title": "Consistency Test Task",
            "task_list_id": str(task_list.id),
            "assigned_to_id": str(assignee.id),
            "status": "pending",
        }
        task_response = client.post("/api/v1/tasks", json=task_data)
        assert task_response.status_code == 201
        task = task_response.json()

        # Update task and verify consistency
        update_data = {"status": "completed"}
        update_response = client.patch(f"/api/v1/tasks/{task['id']}", json=update_data)
        assert update_response.status_code == 200

        # Verify the update is reflected in get and list operations
        get_response = client.get(f"/api/v1/tasks/{task['id']}")
        assert get_response.status_code == 200
        updated_task = get_response.json()
        assert updated_task["status"] == "completed"

        list_response = client.get(f"/api/v1/tasks?task_list_id={task_list.id}")
        assert list_response.status_code == 200
        tasks_list = list_response.json()
        found_task = next(
            (t for t in tasks_list["items"] if t["id"] == task["id"]), None
        )
        assert found_task is not None
        assert found_task["status"] == "completed"

        # Test filtering by the updated status
        completed_response = client.get("/api/v1/tasks?status=completed")
        assert completed_response.status_code == 200
        completed_tasks = completed_response.json()
        assert any(t["id"] == task["id"] for t in completed_tasks["items"])
