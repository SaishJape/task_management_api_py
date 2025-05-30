from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.models.task import TaskCreate, TaskInDB, TaskResponse, TaskAssign, TaskStatusUpdate
from app.models.user import UserInDB
from app.api.dependencies import get_current_user
from app.database.db_manager import db_manager

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task_data: TaskCreate, current_user: UserInDB = Depends(get_current_user)):
    task_in_db = TaskInDB(
        title=task_data.title,
        description=task_data.description,
        created_by=current_user.id
    )
    
    task_id = db_manager.create_task(task_in_db)
    
    return TaskResponse(
        id=task_id,
        title=task_data.title,
        description=task_data.description,
        created_at=task_in_db.created_at,
        assigned_to=None,
        created_by=current_user.id,
        status=task_in_db.status
    )

@router.get("/", response_model=List[TaskResponse])
async def get_my_tasks(current_user: UserInDB = Depends(get_current_user)):
    tasks = db_manager.get_tasks_by_user(current_user.id)
    
    # Convert from TaskInDB to TaskResponse
    response_tasks = [
        TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            created_at=task.created_at,
            assigned_to=task.assigned_to,
            created_by=task.created_by,
            status=task.status
        ) for task in tasks
    ]
    
    return response_tasks

@router.post("/assign", status_code=status.HTTP_200_OK)
async def assign_task(task_assign: TaskAssign, current_user: UserInDB = Depends(get_current_user)):
    # Get the task
    task = db_manager.get_task_by_id(task_assign.task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user has permissions to assign this task
    if task.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to assign this task"
        )
    
    # Check if target user exists
    target_user = db_manager.get_user_by_id(task_assign.user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target user not found"
        )
    
    # Assign the task
    success = db_manager.assign_task(task_assign.task_id, task_assign.user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to assign task"
        )
    
    return {"message": "Task assigned successfully"}

@router.post("/update-status", status_code=status.HTTP_200_OK)
async def update_task_status(task_update: TaskStatusUpdate, current_user: UserInDB = Depends(get_current_user)):
    # Get the task
    task = db_manager.get_task_by_id(task_update.task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user is the assigned user
    if task.assigned_to != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the assigned user can update the task status"
        )
    
    # Validate status (we removed in-progress)
    if task_update.status not in ["pending", "completed", "cancelled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status. Must be one of: pending, completed, cancelled"
        )
    
    # Update the status
    success = db_manager.update_task_status(task_update.task_id, task_update.status)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update task status"
        )
    
    return {"message": f"Task status updated to {task_update.status}"}