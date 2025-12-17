from typing import Optional, List
from datetime import datetime
from enum import Enum

from app.core.database import db
from app.services.user_service import get_user_by_id
from app.services.client_service import get_client_by_user_id, record_visit as record_client_visit

class AttendanceMethod(str, Enum):
    CARD = "card"
    MANUAL = "manual"
    APP = "app"

def record_attendance(
    client_user_id: int, 
    method: AttendanceMethod = AttendanceMethod.MANUAL,
    recorded_by: Optional[int] = None
) -> Optional[dict]:
    client = get_client_by_user_id(client_user_id)
    if not client:
        raise ValueError("Клиент не найден")
    
    updated_client = record_client_visit(client.id)
    if not updated_client:
        raise ValueError("Нет действующего абонемента или посещения закончились")
    
    attendance_record = {
        "id": len(db.db["attendances"]) + 1,
        "client_id": client.id,
        "check_in_time": datetime.now(),
        "check_out_time": None,
        "method": method,
        "recorded_by": recorded_by,
        "visit_number": updated_client.visits_left + 1
    }
    
    db.db["attendances"].append(attendance_record)
    
    return {
        "attendance": attendance_record,
        "client": updated_client,
        "visits_left": updated_client.visits_left
    }

def record_check_out(client_user_id: int) -> Optional[dict]:
    client = get_client_by_user_id(client_user_id)
    if not client:
        raise ValueError("Клиент не найден")
    
    latest_check_in = None
    for attendance in reversed(db.db["attendances"]):
        if attendance["client_id"] == client.id and attendance["check_out_time"] is None:
            latest_check_in = attendance
            break
    
    if not latest_check_in:
        raise ValueError("Нет активного посещения")
    
    latest_check_in["check_out_time"] = datetime.now()
    
    return latest_check_in

def get_client_attendance(client_user_id: int, limit: int = 50) -> List[dict]:
    client = get_client_by_user_id(client_user_id)
    if not client:
        return []
    
    attendances = []
    for attendance in db.db["attendances"]:
        if attendance["client_id"] == client.id:
            if attendance["recorded_by"]:
                user = get_user_by_id(attendance["recorded_by"])
                attendance["recorded_by_name"] = user.full_name if user else "Неизвестно"
            attendances.append(attendance)
    
    attendances.sort(key=lambda x: x["check_in_time"], reverse=True)
    
    return attendances[:limit]

def get_todays_attendance() -> List[dict]:
    today = datetime.now().date()
    result = []
    
    for attendance in db.db["attendances"]:
        if attendance["check_in_time"].date() == today:
            client = get_client_by_user_id(attendance["client_id"])
            if client:
                user = get_user_by_id(client.user_id)
                if user:
                    attendance["client_name"] = user.full_name or user.username
                    attendance["client_phone"] = user.phone
                    result.append(attendance)
    
    result.sort(key=lambda x: x["check_in_time"], reverse=True)
    return result

def get_active_visits() -> List[dict]:
    result = []
    current_time = datetime.now()
    
    for attendance in db.db["attendances"]:
        if attendance["check_out_time"] is None:
            time_inside = current_time - attendance["check_in_time"]
            if time_inside.total_seconds() <= 5 * 3600:
                client = get_client_by_user_id(attendance["client_id"])
                if client:
                    user = get_user_by_id(client.user_id)
                    if user:
                        attendance["client_name"] = user.full_name or user.username
                        attendance["client_phone"] = user.phone
                        attendance["time_inside_minutes"] = int(time_inside.total_seconds() / 60)
                        result.append(attendance)
    
    return result
