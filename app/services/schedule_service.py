from typing import Optional, List
from datetime import datetime, timedelta
from app.api.models.schedule import Workout, WorkoutCreate, WorkoutUpdate, WorkoutType, Location
from app.core.database import db
from app.services.user_service import get_user_by_id

def check_workout_conflict(workout: WorkoutCreate) -> Optional[str]:
    new_start = workout.start_time
    new_end = new_start + timedelta(minutes=workout.duration)
    
    for existing_workout in db.db["workouts"]:
        if existing_workout.is_cancelled:
            continue
            
        existing_start = existing_workout.start_time
        existing_end = existing_start + timedelta(minutes=existing_workout.duration)
        
        if not (new_end <= existing_start or new_start >= existing_end):
            if existing_workout.trainer_id == workout.trainer_id:
                return f"Тренер уже занят в это время (занятие ID: {existing_workout.id})"
            
            if existing_workout.location == workout.location:
                return f"Локация '{workout.location}' уже занята в это время (занятие ID: {existing_workout.id})"
    
    return None

def create_workout(workout_data: WorkoutCreate) -> Workout:
    trainer = get_user_by_id(workout_data.trainer_id)
    if not trainer or trainer.role != "trainer":
        raise ValueError("Указанный тренер не найден или не является тренером")
    
    conflict = check_workout_conflict(workout_data)
    if conflict:
        raise ValueError(f"Конфликт расписания: {conflict}")
    
    workout_dict = workout_data.model_dump()
    workout_dict["id"] = len(db.db["workouts"]) + 1
    workout_dict["current_participants"] = 0
    workout_dict["is_cancelled"] = False
    workout_dict["created_at"] = datetime.now()
    workout_dict["updated_at"] = datetime.now()
    
    workout = Workout(**workout_dict)
    db.db["workouts"].append(workout)
    return workout

def get_workout(workout_id: int) -> Optional[Workout]:
    for workout in db.db["workouts"]:
        if workout.id == workout_id:
            return workout
    return None

def get_workouts_by_trainer(trainer_id: int, date: Optional[datetime] = None) -> List[Workout]:
    result = []
    for workout in db.db["workouts"]:
        if workout.trainer_id == trainer_id and not workout.is_cancelled:
            if date:
                if workout.start_time.date() == date.date():
                    result.append(workout)
            else:
                result.append(workout)
    
    result.sort(key=lambda x: x.start_time)
    return result

def get_workouts_by_date(date: datetime) -> List[Workout]:
    result = []
    for workout in db.db["workouts"]:
        if workout.start_time.date() == date.date() and not workout.is_cancelled:
            result.append(workout)
    
    result.sort(key=lambda x: x.start_time)
    return result

def update_workout(workout_id: int, update_data: WorkoutUpdate) -> Optional[Workout]:
    for i, workout in enumerate(db.db["workouts"]):
        if workout.id == workout_id:
            if update_data.start_time or update_data.duration:
                temp_workout = workout.model_copy()
                
                if update_data.start_time:
                    temp_workout.start_time = update_data.start_time
                if update_data.duration:
                    temp_workout.duration = update_data.duration
                
                conflict = check_workout_conflict(temp_workout)
                if conflict:
                    raise ValueError(f"Конфликт расписания при обновлении: {conflict}")
            
            for field, value in update_data.model_dump(exclude_unset=True).items():
                setattr(workout, field, value)
            
            workout.updated_at = datetime.now()
            db.db["workouts"][i] = workout
            return workout
    
    return None

def cancel_workout(workout_id: int) -> Optional[Workout]:
    for i, workout in enumerate(db.db["workouts"]):
        if workout.id == workout_id:
            workout.is_cancelled = True
            workout.updated_at = datetime.now()
            db.db["workouts"][i] = workout
            
            workout.current_participants = 0
            return workout
    
    return None

def book_workout(workout_id: int, client_id: int) -> Optional[Workout]:
    workout = get_workout(workout_id)
    if not workout or workout.is_cancelled:
        raise ValueError("Занятие не найдено или отменено")
    
    if workout.current_participants >= workout.max_participants:
        raise ValueError("Нет свободных мест")
    
    for booking in db.db["workout_bookings"]:
        if booking["workout_id"] == workout_id and booking["client_id"] == client_id:
            raise ValueError("Клиент уже записан на это занятие")
    
    db.db["workout_bookings"].append({
        "id": len(db.db["workout_bookings"]) + 1,
        "workout_id": workout_id,
        "client_id": client_id,
        "booked_at": datetime.now(),
        "attended": False
    })
    
    workout.current_participants += 1
    return workout

def get_client_workouts(client_id: int, future_only: bool = True) -> List[Workout]:
    result = []
    current_time = datetime.now()
    
    for booking in db.db["workout_bookings"]:
        if booking["client_id"] == client_id:
            workout = get_workout(booking["workout_id"])
            if workout:
                if not future_only or workout.start_time > current_time:
                    result.append(workout)
    
    result.sort(key=lambda x: x.start_time)
    return result

def get_workout_participants(workout_id: int) -> List[dict]:
    participants = []
    for booking in db.db["workout_bookings"]:
        if booking["workout_id"] == workout_id:
            from app.services.user_service import get_user_by_id
            user = get_user_by_id(booking["client_id"])
            if user:
                participants.append({
                    "user_id": user.id,
                    "username": user.username,
                    "full_name": user.full_name,
                    "booked_at": booking["booked_at"],
                    "attended": booking.get("attended", False)
                })
    
    return participants

def init_schedule_data():
    if not db.db["workouts"]:
        from datetime import datetime, timedelta
        
        tomorrow = datetime.now() + timedelta(days=1)
        
        workout1 = WorkoutCreate(
            trainer_id=2,
            workout_type=WorkoutType.PERSONAL,
            location=Location.GYM,
            start_time=tomorrow.replace(hour=10, minute=0, second=0),
            duration=60,
            max_participants=1,
            description="Индивидуальная тренировка"
        )
        create_workout(workout1)
        
        workout2 = WorkoutCreate(
            trainer_id=2,
            workout_type=WorkoutType.GROUP,
            location=Location.GROUP_ROOM,
            start_time=tomorrow.replace(hour=12, minute=0, second=0),
            duration=90,
            max_participants=20,
            description="Групповая аэробика"
        )
        create_workout(workout2)
        
        workout3 = WorkoutCreate(
            trainer_id=2,
            workout_type=WorkoutType.SWIMMING,
            location=Location.POOL,
            start_time=tomorrow.replace(hour=15, minute=0, second=0),
            duration=45,
            max_participants=15,
            description="Аквааэробика"
        )
        create_workout(workout3)
        
        workout4_dict = WorkoutCreate(
            trainer_id=0,
            workout_type=WorkoutType.OPEN_GYM,
            location=Location.GYM,
            start_time=tomorrow.replace(hour=18, minute=0, second=0),
            duration=120,
            max_participants=30,
            description="Свободное посещение зала"
        ).model_dump()
        workout4_dict["id"] = 4
        workout4_dict["current_participants"] = 0
        workout4_dict["is_cancelled"] = False
        workout4_dict["created_at"] = datetime.now()
        workout4_dict["updated_at"] = datetime.now()
        db.db["workouts"].append(Workout(**workout4_dict))
        
        print("Инициализированы тестовые данные расписания")

#init_schedule_data()
