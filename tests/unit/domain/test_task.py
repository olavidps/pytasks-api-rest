"""Unit tests for Task domain model."""

from datetime import datetime
from uuid import uuid4

from app.domain.models.task import Task, TaskPriority, TaskStatus


class TestTask:
    """Unit tests for Task domain entity."""

    def test_create_task_success(self):
        """Test successful task creation with valid data."""
        task_id = uuid4()
        task_list_id = uuid4()
        title = "Test Task"
        description = "Test Description"

        task = Task(
            id=task_id,
            title=title,
            description=description,
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            task_list_id=task_list_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert task.id == task_id
        assert task.title == title
        assert task.description == description
        assert task.status == TaskStatus.PENDING
        assert task.priority == TaskPriority.MEDIUM
        assert task.task_list_id == task_list_id
        assert task.assigned_user_id is None

    def test_task_mark_as_completed(self):
        """Test marking task as completed."""
        task = Task(
            id=uuid4(),
            title="Test Task",
            description="Test Description",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            task_list_id=uuid4(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        completed_task = task.mark_as_completed()

        assert completed_task.status == TaskStatus.COMPLETED
        assert completed_task.id == task.id
        assert completed_task.title == task.title

    def test_task_mark_as_in_progress(self):
        """Test marking task as in progress."""
        task = Task(
            id=uuid4(),
            title="Test Task",
            description="Test Description",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            task_list_id=uuid4(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        in_progress_task = task.mark_as_in_progress()

        assert in_progress_task.status == TaskStatus.IN_PROGRESS
        assert in_progress_task.id == task.id
        assert in_progress_task.title == task.title

    def test_task_assign_to_user(self):
        """Test assigning task to a user."""
        task = Task(
            id=uuid4(),
            title="Test Task",
            description="Test Description",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            task_list_id=uuid4(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        user_id = uuid4()
        assigned_task = task.assign_to_user(user_id)

        assert assigned_task.assigned_user_id == user_id
        assert assigned_task.id == task.id
        assert assigned_task.title == task.title

    def test_task_unassign(self):
        """Test unassigning task from user."""
        user_id = uuid4()
        task = Task(
            id=uuid4(),
            title="Test Task",
            description="Test Description",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            task_list_id=uuid4(),
            assigned_user_id=user_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        unassigned_task = task.assign_to_user(None)

        assert unassigned_task.assigned_user_id is None
        assert unassigned_task.id == task.id
        assert unassigned_task.title == task.title

    def test_task_update_priority(self):
        """Test updating task priority."""
        task = Task(
            id=uuid4(),
            title="Test Task",
            description="Test Description",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            task_list_id=uuid4(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        high_priority_task = task.change_priority(TaskPriority.HIGH)

        assert high_priority_task.priority == TaskPriority.HIGH
        assert high_priority_task.id == task.id
        assert high_priority_task.title == task.title

    def test_task_is_overdue_with_due_date_past(self):
        """Test is_overdue property when due date is in the past."""
        from datetime import datetime, timedelta, timezone

        past_date = datetime.now(timezone.utc) - timedelta(days=1)
        task = Task(
            id=uuid4(),
            title="Overdue Task",
            description="This task is overdue",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            task_list_id=uuid4(),
            due_date=past_date,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert task.is_overdue is True

    def test_task_is_overdue_with_due_date_future(self):
        """Test is_overdue property when due date is in the future."""
        from datetime import datetime, timedelta, timezone

        future_date = datetime.now(timezone.utc) + timedelta(days=1)
        task = Task(
            id=uuid4(),
            title="Future Task",
            description="This task is not overdue",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            task_list_id=uuid4(),
            due_date=future_date,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert task.is_overdue is False

    def test_task_is_overdue_without_due_date(self):
        """Test is_overdue property when no due date is set."""
        task = Task(
            id=uuid4(),
            title="No Due Date Task",
            description="This task has no due date",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            task_list_id=uuid4(),
            due_date=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert task.is_overdue is False

    def test_task_is_overdue_when_completed(self):
        """Test is_overdue property for completed tasks (should not be overdue)."""
        from datetime import datetime, timedelta, timezone

        past_date = datetime.now(timezone.utc) - timedelta(days=1)
        task = Task(
            id=uuid4(),
            title="Completed Overdue Task",
            description="This task was completed even though overdue",
            status=TaskStatus.COMPLETED,
            priority=TaskPriority.MEDIUM,
            task_list_id=uuid4(),
            due_date=past_date,
            completed_at=datetime.now(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert task.is_overdue is False  # Completed tasks are not considered overdue

    def test_task_is_completed_property(self):
        """Test is_completed property."""
        # Pending task
        pending_task = Task(
            id=uuid4(),
            title="Pending Task",
            description="This task is pending",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            task_list_id=uuid4(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert pending_task.is_completed is False

        # Completed task
        completed_task = Task(
            id=uuid4(),
            title="Completed Task",
            description="This task is completed",
            status=TaskStatus.COMPLETED,
            priority=TaskPriority.MEDIUM,
            task_list_id=uuid4(),
            completed_at=datetime.now(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert completed_task.is_completed is True

    def test_task_update_details(self):
        """Test updating task details."""
        task = Task(
            id=uuid4(),
            title="Original Title",
            description="Original Description",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            task_list_id=uuid4(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        updated_task = task.update_details(
            title="Updated Title", description="Updated Description"
        )

        assert updated_task.title == "Updated Title"
        assert updated_task.description == "Updated Description"
        assert updated_task.id == task.id
        assert updated_task.status == task.status

    def test_task_mark_as_pending(self):
        """Test marking task as pending."""
        task = Task(
            id=uuid4(),
            title="In Progress Task",
            description="This task is in progress",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.MEDIUM,
            task_list_id=uuid4(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        pending_task = task.mark_as_pending()

        assert pending_task.status == TaskStatus.PENDING
        assert pending_task.id == task.id
        assert pending_task.completed_at is None

    def test_task_state_transitions(self):
        """Test valid task state transitions."""
        task = Task(
            id=uuid4(),
            title="State Transition Task",
            description="Testing state transitions",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            task_list_id=uuid4(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # PENDING -> IN_PROGRESS
        in_progress_task = task.mark_as_in_progress()
        assert in_progress_task.status == TaskStatus.IN_PROGRESS

        # IN_PROGRESS -> COMPLETED
        completed_task = in_progress_task.mark_as_completed()
        assert completed_task.status == TaskStatus.COMPLETED
        assert completed_task.completed_at is not None

        # COMPLETED -> PENDING (reopening)
        reopened_task = completed_task.mark_as_pending()
        assert reopened_task.status == TaskStatus.PENDING
        assert reopened_task.completed_at is None
