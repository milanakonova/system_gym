"""
API endpoints для посещений
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from scr.db.database import get_db
from scr.db.models import User, UserRole, Visit
from scr.core.dependencies import get_current_active_user, require_role

router = APIRouter(prefix="/api/attendance", tags=["attendance"])


@router.get("/me/history")
async def get_my_visit_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.CLIENT))
):
    """Получение истории посещений текущего клиента"""
    visits = db.query(Visit).filter(Visit.client_id == current_user.id).order_by(Visit.check_in_time.desc()).all()
    
    history = []
    for visit in visits:
        history.append({
            "id": str(visit.id),
            "check_in_time": visit.check_in_time.isoformat() if visit.check_in_time else None,
            "check_out_time": visit.check_out_time.isoformat() if visit.check_out_time else None,
            "visit_type": visit.visit_type,
            "method": "manual"  # По умолчанию
        })
    
    return {"history": history}

