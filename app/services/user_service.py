from typing import Optional, List
from app.api.models.user import UserCreate, UserInDB, Role
from app.core.security import get_password_hash, verify_password
from app.core.database import db
from datetime import datetime

def init_db():
    if not db.db["users"]:
        admin_user = UserCreate(
            username="admin",
            email="admin@gym.ru",
            password="admin123",
            full_name="Администратор Системы",
            phone="+79160000000",
            role=Role.ADMIN
        )
        create_user(admin_user)
        
        trainer_user = UserCreate(
            username="trainer1",
            email="trainer@gym.ru",
            password="trainer123",
            full_name="Иван Тренеров",
            phone="+79161111111",
            role=Role.TRAINER
        )
        create_user(trainer_user)
        
        client_user = UserCreate(
            username="client1",
            email="client@gym.ru",
            password="client123",
            full_name="Петр Клиентов",
            phone="+79162222222",
            role=Role.CLIENT
        )
        create_user(client_user)
        
        print("Инициализирована база данных с тестовыми пользователями")

def create_user(user: UserCreate) -> UserInDB:
    for existing_user in db.db["users"]:
        if existing_user.username == user.username:
            raise ValueError("Пользователь с таким логином уже существует")
        if existing_user.email == user.email:
            raise ValueError("Пользователь с таким email уже существует")
    
    user_dict = user.model_dump()
    user_dict["id"] = len(db.db["users"]) + 1
    user_dict["hashed_password"] = get_password_hash(user.password)
    user_dict.pop("password")
    
    user_in_db = UserInDB(**user_dict)
    db.db["users"].append(user_in_db)
    
    if user.role == Role.CLIENT:
        from app.services.client_service import create_client
        create_client(user_in_db.id)
    
    return user_in_db

def get_user_by_username(username: str) -> Optional[UserInDB]:
    for user in db.db["users"]:
        if user.username == username:
            return user
    return None

def get_user_by_id(user_id: int) -> Optional[UserInDB]:
    for user in db.db["users"]:
        if user.id == user_id:
            return user
    return None

def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    user = get_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def get_all_users() -> List[UserInDB]:
    return db.db["users"]

# init_db()
