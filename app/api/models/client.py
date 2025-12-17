from pydantic import BaseModel
from typing import Optional
from enum import Enum

class ServiceType(str, Enum):
    TRAINER = "trenirovka_s_trenerom"
    GROUP = "gruppovye_zanyatiya"
    EQUIPMENT = "arenda_trenazherov"
    POOL = "plavatelny_bassein"

class Service(BaseModel):
    id: int
    name: str
    price: float
    duration: int
    service_type: ServiceType

class ClientBase(BaseModel):
    user_id: int
    date_of_birth: Optional[str] = None
    medical_notes: Optional[str] = None

class Client(ClientBase):
    id: int
    has_subscription: bool = False
    visits_left: int = 0
    subscription_type: Optional[ServiceType] = None
    subscription_end_date: Optional[str] = None
