from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import List

from app.api.models.user import UserInDB
from app.api.dependencies import get_current_active_user, require_admin, require_manager
from app.services.attendance_service import (
    record_attendance, record_check_out, get_client_attendance,
    get_todays_attendance, get_active_visits, AttendanceMethod
)

router = APIRouter()

@router.post("/check-in")
async def check_in_client(
    client_user_id: int,
    method: AttendanceMethod = AttendanceMethod.MANUAL,
    current_user: UserInDB = Depends(get_current_active_user)
):
    if current_user.role == "client" and current_user.id != client_user_id:
        raise HTTPException(status_code=403, detail="Клиент может отмечать только себя")
    
    if current_user.role not in ["admin", "manager", "client"]:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    try:
        result = record_attendance(
            client_user_id, 
            method, 
            recorded_by=current_user.id if current_user.role != "client" else None
        )
        return {
            "message": "Вход успешно зафиксирован",
            "attendance_id": result["attendance"]["id"],
            "check_in_time": result["attendance"]["check_in_time"],
            "visits_left": result["visits_left"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/check-out")
async def check_out_client(
    client_user_id: int,
    current_user: UserInDB = Depends(require_manager)
):
    try:
        attendance = record_check_out(client_user_id)
        return {
            "message": "Выход успешно зафиксирован",
            "attendance_id": attendance["id"],
            "check_in_time": attendance["check_in_time"],
            "check_out_time": attendance["check_out_time"],
            "duration_minutes": int((attendance["check_out_time"] - attendance["check_in_time"]).total_seconds() / 60)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me/history")
async def get_my_attendance_history(
    current_user: UserInDB = Depends(get_current_active_user)
):
    if current_user.role != "client":
        raise HTTPException(status_code=403, detail="Только для клиентов")
    
    history = get_client_attendance(current_user.id)
    return {
        "client_id": current_user.id,
        "total_visits": len(history),
        "history": history
    }

@router.get("/client/{client_user_id}/history")
async def get_client_attendance_history(
    client_user_id: int,
    current_user: UserInDB = Depends(require_manager)
):
    history = get_client_attendance(client_user_id)
    return {
        "client_id": client_user_id,
        "total_visits": len(history),
        "history": history
    }

@router.get("/today", dependencies=[Depends(require_manager)])
async def get_today_attendance():
    return {
        "date": datetime.now().date(),
        "visits": get_todays_attendance(),
        "total_today": len(get_todays_attendance())
    }

@router.get("/active", dependencies=[Depends(require_manager)])
async def get_active_visits_list():
    active_visits = get_active_visits()
    return {
        "active_count": len(active_visits),
        "visits": active_visits
    }

@router.get("/stats")
async def get_attendance_stats(current_user: UserInDB = Depends(require_admin)):
    from app.core.database import db
    from datetime import datetime, timedelta
    
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    total_visits = len(db.db["attendances"])
    visits_today = len([a for a in db.db["attendances"] if a["check_in_time"].date() == today])
    visits_week = len([a for a in db.db["attendances"] if a["check_in_time"].date() >= week_ago])
    visits_month = len([a for a in db.db["attendances"] if a["check_in_time"].date() >= month_ago])
    
    methods_stats = {}
    for attendance in db.db["attendances"]:
        method = attendance.get("method", "manual")
        methods_stats[method] = methods_stats.get(method, 0) + 1
    
    return {
        "total_visits": total_visits,
        "visits_today": visits_today,
        "visits_last_7_days": visits_week,
        "visits_last_30_days": visits_month,
        "methods": methods_stats,
        "active_now": len(get_active_visits())
    }
