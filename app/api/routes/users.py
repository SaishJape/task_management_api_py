from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.models.user import UserInDB, UserResponse
from app.api.dependencies import get_current_user
from app.database.db_manager import db_manager

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/by-email", response_model=UserResponse)
async def get_user_by_email(email: str, current_user: UserInDB = Depends(get_current_user)):
    """
    Get user information by email address.
    Only authenticated users can fetch other users' information.
    """
    user = db_manager.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email not found"
        )
    
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        created_at=user.created_at
    )

@router.get("/", response_model=List[UserResponse])
async def get_users(current_user: UserInDB = Depends(get_current_user)):
    """
    Get a list of all users.
    Only authenticated users can see the list of users.
    """
    # In a real application, you might want to add pagination here
    # and restrict this endpoint to admin users
    users = db_manager.get_all_users()
    
    return [
        UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            created_at=user.created_at
        ) for user in users
    ]