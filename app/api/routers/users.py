from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.api.models.user import UserInDB
from app.api.dependencies import get_current_active_user, require_admin
from app.services.user_service import get_all_users, get_user_by_id

router = APIRouter()

@router.get("/me", response_model=UserInDB)
async def read_users_me(current_user: UserInDB = Depends(get_current_active_user)):
    return current_user

@router.get("/", response_model=List[UserInDB], dependencies=[Depends(require_admin)])
async def read_all_users():
    return get_all_users()

@router.get("/{user_id}", response_model=UserInDB)
async def read_user(user_id: int, current_user: UserInDB = Depends(get_current_active_user)):
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user
