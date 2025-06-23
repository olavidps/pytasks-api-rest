from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.task import Task, TaskPriority, TaskStatus
from app.domain.models.task_list import TaskList
from app.domain.models.user import User


class DataFactory:
    """Factory for creating test data entities."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(
        self,
        email: Optional[str] = None,
        username: Optional[str] = None,
        full_name: Optional[str] = None,
        is_active: bool = True,
    ) -> User:
        user_id = uuid4()
        unique_suffix = user_id.hex[:12]
        email = email or f"user_{unique_suffix}@example.com"
        username = username or f"user_{unique_suffix}"
        full_name = full_name or f"Test User {unique_suffix}"

        user = User(
            id=user_id,
            email=email,
            username=username,
            full_name=full_name,
            is_active=is_active,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def create_task_list(
        self,
        owner: User,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_active: bool = True,
    ) -> TaskList:
        task_list_id = uuid4()
        name = name or f"Test Task List {task_list_id.hex[:8]}"
        description = description or f"Task list for testing {task_list_id.hex[:8]}"

        task_list = TaskList(
            id=task_list_id,
            name=name,
            description=description,
            owner_id=owner.id,
            is_active=is_active,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.session.add(task_list)
        await self.session.commit()
        await self.session.refresh(task_list)
        return task_list

    async def create_task(
        self,
        task_list: TaskList,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: TaskStatus = TaskStatus.PENDING,
        priority: TaskPriority = TaskPriority.MEDIUM,
        assigned_user: Optional[User] = None,
        due_date: Optional[datetime] = None,
    ) -> Task:
        task_id = uuid4()
        title = title or f"Test Task {task_id.hex[:8]}"
        description = description or f"Task for testing {task_id.hex[:8]}"

        task = Task(
            id=task_id,
            title=title,
            description=description,
            status=status,
            priority=priority,
            task_list_id=task_list.id,
            assigned_user_id=assigned_user.id if assigned_user else None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            due_date=due_date,
        )
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def create_multiple_users(self, count: int = 5) -> List[User]:
        users = []
        for i in range(count):
            user = await self.create_user(
                email=f"user{i}@example.com", username=f"user{i}", full_name=f"User {i}"
            )
            users.append(user)
        return users

    async def create_multiple_tasks(
        self, task_list: TaskList, count: int = 10
    ) -> List[Task]:
        tasks = []
        statuses = [TaskStatus.PENDING, TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED]
        priorities = [TaskPriority.LOW, TaskPriority.MEDIUM, TaskPriority.HIGH]

        for i in range(count):
            task = await self.create_task(
                task_list=task_list,
                title=f"Test Task {i}",
                description=f"Task {i} for testing",
                status=statuses[i % len(statuses)],
                priority=priorities[i % len(priorities)],
            )
            tasks.append(task)
        return tasks
