from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.api.models.user import UserInDB
from app.api.models.client import Client, ServiceType, Service
from app.api.dependencies import get_current_active_user, require_admin, require_manager
from app.services.client_service import get_client_by_user_id, get_all_clients, update_client_subscription, record_visit

router = APIRouter()

services = [
    Service(id=1, name="Тренировка с тренером", price=3000, duration=60, service_type=ServiceType.TRAINER),
    Service(id=2, name="Групповые занятия", price=2000, duration=45, service_type=ServiceType.GROUP),
    Service(id=3, name="Аренда тренажеров", price=1500, duration=90, service_type=ServiceType.EQUIPMENT),
    Service(id=4, name="Плавательный бассейн", price=2500, duration=60, service_type=ServiceType.POOL),
]

@router.get("/me", response_model=Client)
async def get_my_client_info(current_user: UserInDB = Depends(get_current_active_user)):
    if current_user.role != "client":
        raise HTTPException(status_code=403, detail="Только для клиентов")
    
    client = get_client_by_user_id(current_user.id)
    if not client:
        raise HTTPException(status_code=404, detail="Информация о клиенте не найдена")
    return client

@router.get("/", response_model=List[Client], dependencies=[Depends(require_manager)])
async def get_all_clients_info():
    return get_all_clients()

@router.get("/services", response_model=List[Service])
async def get_all_services():
    return services

@router.post("/{client_id}/subscription")
async def buy_subscription(client_id: int, service_type: ServiceType, visits: int = 10, 
                          current_user: UserInDB = Depends(require_manager)):
    client = update_client_subscription(client_id, service_type, visits)
    if not client:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    return {"message": "Абонемент успешно оформлен", "client": client}

@router.post("/me/check-in")
async def check_in(current_user: UserInDB = Depends(get_current_active_user)):
    if current_user.role != "client":
        raise HTTPException(status_code=403, detail="Только для клиентов")
    
    client = get_client_by_user_id(current_user.id)
    if not client:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    
    updated_client = record_visit(client.id)
    if not updated_client:
        raise HTTPException(status_code=400, detail="Нет действующего абонемента или посещения закончились")
    
    return {"message": "Посещение зафиксировано", "visits_left": updated_client.visits_left}
