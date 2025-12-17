from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime
from typing import List, Optional

from app.api.models.user import UserInDB
from app.api.models.schedule import (
    Workout, WorkoutCreate, WorkoutUpdate, 
    WorkoutBooking, WorkoutType, Location
)
from app.api.dependencies import get_current_active_user, require_admin, require_trainer
from app.services.schedule_service import (
    create_workout, get_workout, get_workouts_by_trainer,
    get_workouts_by_date, update_workout, cancel_workout, 
    book_workout, get_client_workouts, get_workout_participants
)

router = APIRouter()

@router.post("/", response_model=Workout, dependencies=[Depends(require_trainer)])
async def create_new_workout(
    workout_data: WorkoutCreate,
    current_user: UserInDB = Depends(get_current_active_user)
):
    try:
        if current_user.role == "trainer" and current_user.id != workout_data.trainer_id:
            raise HTTPException(status_code=403, detail="Тренер может создавать только свои занятия")
        
        workout = create_workout(workout_data)
        return workout
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[Workout])
async def get_all_workouts(
    date: Optional[datetime] = Query(None, description="Фильтр по дате"),
    workout_type: Optional[WorkoutType] = Query(None, description="Тип занятия"),
    location: Optional[Location] = Query(None, description="Локация"),
    current_user: UserInDB = Depends(get_current_active_user)
):
    from app.core.database import db
    
    workouts = []
    
    if date:
        workouts = get_workouts_by_date(date)
    else:
        workouts = [w for w in db.db["workouts"] if not w.is_cancelled]
        workouts.sort(key=lambda x: x.start_time)
    
    if workout_type:
        workouts = [w for w in workouts if w.workout_type == workout_type]
    
    return workouts

@router.get("/{workout_id}", response_model=Workout)
async def get_workout_by_id(
    workout_id: int,
    current_user: UserInDB = Depends(get_current_active_user)
):
    workout = get_workout(workout_id)
    if not workout or workout.is_cancelled:
        raise HTTPException(status_code=404, detail="Занятие не найдено")
    return workout

@router.put("/{workout_id}", response_model=Workout)
async def update_workout_by_id(
    workout_id: int,
    update_data: WorkoutUpdate,
    current_user: UserInDB = Depends(get_current_active_user)
):
    workout = get_workout(workout_id)
    if not workout:
        raise HTTPException(status_code=404, detail="Занятие не найдено")
    
    if current_user.role != "admin" and current_user.id != workout.trainer_id:
        raise HTTPException(status_code=403, detail="Недостаточно прав для изменения занятия")
    
    try:
        updated_workout = update_workout(workout_id, update_data)
        if not updated_workout:
            raise HTTPException(status_code=404, detail="Занятие не найдено")
        return updated_workout
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{workout_id}", dependencies=[Depends(require_admin)])
async def delete_workout(workout_id: int):
    workout = cancel_workout(workout_id)
    if not workout:
        raise HTTPException(status_code=404, detail="Занятие не найдено")
    return {"message": "Занятие отменено"}

@router.get("/trainer/{trainer_id}", response_model=List[Workout])
async def get_trainer_schedule(
    trainer_id: int,
    date: Optional[datetime] = Query(None),
    current_user: UserInDB = Depends(get_current_active_user)
):
    workouts = get_workouts_by_trainer(trainer_id, date)
    return workouts

@router.get("/trainer/me/schedule", response_model=List[Workout])
async def get_my_schedule(
    date: Optional[datetime] = Query(None),
    current_user: UserInDB = Depends(get_current_active_user)
):
    if current_user.role != "trainer":
        raise HTTPException(status_code=403, detail="Только для тренеров")
    
    workouts = get_workouts_by_trainer(current_user.id, date)
    return workouts

@router.post("/{workout_id}/book", response_model=Workout)
async def book_for_workout(
    workout_id: int,
    booking_data: WorkoutBooking,
    current_user: UserInDB = Depends(get_current_active_user)
):
    if current_user.role == "client" and current_user.id != booking_data.client_id:
        raise HTTPException(status_code=403, detail="Клиент может записывать только себя")
    
    if current_user.role not in ["admin", "manager", "client"]:
        raise HTTPException(status_code=403, detail="Недостаточно прав для записи")
    
    try:
        workout = book_workout(workout_id, booking_data.client_id)
        if not workout:
            raise HTTPException(status_code=404, detail="Занятие не найдено")
        return workout
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/client/me/workouts", response_model=List[Workout])
async def get_my_workouts(
    future_only: bool = Query(True, description="Только будущие занятия"),
    current_user: UserInDB = Depends(get_current_active_user)
):
    if current_user.role != "client":
        raise HTTPException(status_code=403, detail="Только для клиентов")
    
    workouts = get_client_workouts(current_user.id, future_only)
    return workouts

@router.get("/{workout_id}/participants")
async def get_workout_participants_list(
    workout_id: int,
    current_user: UserInDB = Depends(get_current_active_user)
):
    workout = get_workout(workout_id)
    if not workout:
        raise HTTPException(status_code=404, detail="Занятие не найдено")
    
    if (current_user.role == "trainer" and current_user.id != workout.trainer_id and 
        current_user.role not in ["admin", "manager"]):
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    participants = get_workout_participants(workout_id)
    return {"workout_id": workout_id, "participants": participants}
