from typing import Optional, List
from app.api.models.client import Client, ClientBase
from app.core.database import db

def create_client(user_id: int) -> Client:
    client_data = ClientBase(user_id=user_id)
    client_dict = client_data.model_dump()
    client_dict["id"] = len(db.db["clients"]) + 1
    
    client = Client(**client_dict)
    db.db["clients"].append(client)
    return client

def get_client_by_user_id(user_id: int) -> Optional[Client]:
    for client in db.db["clients"]:
        if client.user_id == user_id:
            return client
    return None

def get_client_by_id(client_id: int) -> Optional[Client]:
    for client in db.db["clients"]:
        if client.id == client_id:
            return client
    return None

def update_client_subscription(client_id: int, service_type, visits: int = 10) -> Optional[Client]:
    for client in db.db["clients"]:
        if client.id == client_id:
            client.has_subscription = True
            client.subscription_type = service_type
            client.visits_left = visits
            return client
    return None

def record_visit(client_id: int) -> Optional[Client]:
    for client in db.db["clients"]:
        if client.id == client_id:
            if client.has_subscription and client.visits_left > 0:
                client.visits_left -= 1
                return client
    return None

def get_all_clients() -> List[Client]:
    return db.db["clients"]
