"""Integration tests focusing on entity relationships and cross-repository operations."""

import pytest

from app.domain.models.task import TaskPriority, TaskStatus


class TestDatabaseIntegration:
    """Integration tests focusing on entity relationships and cross-repository operations."""

    @pytest.mark.asyncio
    async def test_cross_entity_relationships(self, test_factory):
        """Test complex relationships between users, task lists, and tasks."""
        # Create users using the factory with unique identifiers
        user_1 = await test_factory.create_user(full_name="User One")
        user_2 = await test_factory.create_user(full_name="User Two")

        # Get repositories from the factory session
        task_list_repo = test_factory.task_list_repo
        task_repo = test_factory.task_repo

        # Create task lists for different users using factory
        created_list_1 = await test_factory.create_task_list(
            owner=user_1, name="User 1 List", description="List owned by user 1"
        )
        created_list_2 = await test_factory.create_task_list(
            owner=user_2, name="User 2 List", description="List owned by user 2"
        )

        # Create tasks for the lists
        await test_factory.create_task(
            task_list=created_list_1,
            title="Task 1 for List 1",
            description="First task",
            status=TaskStatus.PENDING,
            priority=TaskPriority.HIGH,
        )
        await test_factory.create_task(
            task_list=created_list_1,
            title="Task 2 for List 1",
            description="Second task",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.MEDIUM,
        )
        await test_factory.create_task(
            task_list=created_list_2,
            title="Task 1 for List 2",
            description="Single task",
            status=TaskStatus.PENDING,
            priority=TaskPriority.LOW,
        )

        # Test complex relationship queries
        # User 1 owns 1 list
        user_1_lists = await task_list_repo.get_by_owner_id(user_1.id)
        assert len(user_1_lists) == 1

        # User 2 owns 1 list
        user_2_lists = await task_list_repo.get_by_owner_id(user_2.id)
        assert len(user_2_lists) == 1

        # List 1 has 2 tasks
        list_1_tasks = await task_repo.get_by_task_list_id(created_list_1.id)
        assert len(list_1_tasks) == 2

        # List 2 has 1 task
        list_2_tasks = await task_repo.get_by_task_list_id(created_list_2.id)
        assert len(list_2_tasks) == 1

    @pytest.mark.asyncio
    async def test_cascade_operations(self, test_factory):
        """Test cascade behavior when deleting entities with relationships."""
        # Create user and task list using factory
        user = await test_factory.create_user(full_name="Cascade User")

        created_list = await test_factory.create_task_list(
            owner=user, name="Test List", description="List to be deleted"
        )

        # Create multiple tasks in the list using factory
        task_ids = []
        for i in range(3):
            created_task = await test_factory.create_task(
                task_list=created_list,
                title=f"Task {i+1}",
                description=f"Task {i+1} description",
                status=TaskStatus.PENDING,
                priority=TaskPriority.MEDIUM,
            )
            task_ids.append(created_task.id)

        # Get repositories from factory
        task_list_repo = test_factory.task_list_repo
        task_repo = test_factory.task_repo

        # Verify tasks exist
        list_tasks = await task_repo.get_by_task_list_id(created_list.id)
        assert len(list_tasks) == 3

        # Delete task list (should handle FK constraints properly)
        # Note: This tests the database constraint behavior
        # In a real scenario, you might want to delete tasks first or handle cascades
        delete_result = await task_list_repo.delete(created_list.id)
        assert delete_result is True

        # Verify task list is deleted
        found_list = await task_list_repo.get_by_id(created_list.id)
        assert found_list is None

        # Verify tasks still exist but are orphaned (depending on FK constraint setup)
        # This behavior depends on your database schema constraints
        remaining_tasks = await task_repo.get_by_task_list_id(created_list.id)
        assert len(remaining_tasks) == 0  # Assuming CASCADE DELETE or proper cleanup

    @pytest.mark.asyncio
    async def test_transaction_consistency(self, test_factory):
        """Test transaction consistency across multiple repository operations."""
        # Create user, task list, and task using factory
        user = await test_factory.create_user(full_name="Consistency User")

        created_list = await test_factory.create_task_list(
            owner=user,
            name="Consistency Test List",
            description="Testing transaction consistency",
        )

        created_task = await test_factory.create_task(
            task_list=created_list,
            title="Consistency Test Task",
            description="Testing consistency",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
        )

        # Get repositories from factory
        user_repo = test_factory.user_repo
        task_list_repo = test_factory.task_list_repo
        task_repo = test_factory.task_repo

        # Assign task to user
        assigned_task = created_task.assign_to_user(user.id)
        created_task = await task_repo.update(assigned_task)

        # Perform multiple operations in sequence
        # Update task status
        completed_task = created_task.mark_as_completed()
        updated_task = await task_repo.update(completed_task)

        # Update task list
        updated_list = created_list.model_copy(
            update={"name": "Updated Consistency Test List"}
        )
        final_list = await task_list_repo.update(updated_list)

        # Update user
        updated_user = user.update_profile(full_name="Updated Test User")
        final_user = await user_repo.update(updated_user)

        # Verify all changes are consistent
        assert updated_task.status == TaskStatus.COMPLETED
        assert updated_task.completed_at is not None
        assert final_list.name == "Updated Consistency Test List"
        assert final_user.full_name == "Updated Test User"

        # Verify relationships are maintained
        user_tasks = await task_repo.get_by_assigned_user_id(user.id)
        assert len(user_tasks) == 1
        assert user_tasks[0].status == TaskStatus.COMPLETED

        user_lists = await task_list_repo.get_by_owner_id(user.id)
        assert len(user_lists) == 1
        assert user_lists[0].name == "Updated Consistency Test List"
