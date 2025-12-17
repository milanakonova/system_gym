from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class Location(str, Enum):
    GYM = "gym"
    POOL = "pool"
    GROUP_ROOM = "group_room"
    YOGA_ROOM = "yoga_room"

class WorkoutType(str, Enum):
    PERSONAL = "personal"
    GROUP = "group"
    OPEN_GYM = "open_gym"
    SWIMMING = "swimming"

class WorkoutBase(BaseModel):
    trainer_id: int
    workout_type: WorkoutType
    location: Location
    start_time: datetime
    duration: int = Field(..., ge=30, le=180)
    max_participants: int = Field(default=1, ge=1, le=50)
    description: Optional[str] = None

class WorkoutCreate(WorkoutBase):
    pass

class WorkoutUpdate(BaseModel):
    start_time: Optional[datetime] = None
    duration: Optional[int] = None
    max_participants: Optional[int] = None
    description: Optional[str] = None
    is_cancelled: Optional[bool] = None

class Workout(WorkoutBase):
    id: int
    current_participants: int = 0
    is_cancelled: bool = False
    created_at: datetime
    updated_at: datetime

class WorkoutBooking(BaseModel):
    client_id: int
    workout_id: int
