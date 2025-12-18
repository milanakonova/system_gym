"""
API для разовых записей расписания (по конкретной дате)
"""
from typing import List, Optional
from uuid import UUID
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from scr.db.database import get_db
from scr.db.models import (
    User, UserRole,
    GymZone,
    TrainingSession, TrainingSessionParticipant,
)
from scr.core.dependencies import get_current_active_user, require_role
from scr.schemas.training_session import TrainingSessionCreate, TrainingSessionResponse


router = APIRouter(prefix="/api/schedule", tags=["schedule"])


@router.post("", response_model=TrainingSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_training_session(
    payload: TrainingSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.TRAINER))
):
    """Тренер создаёт запись расписания на конкретную дату"""
    if payload.start_time >= payload.end_time:
        raise HTTPException(status_code=400, detail="Время начала должно быть меньше времени окончания")

    zone = db.query(GymZone).filter(GymZone.id == payload.gym_zone_id, GymZone.is_active == True).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Зал не найден")

    # Проверка пересечений у тренера на эту дату
    overlap = db.query(TrainingSession).filter(
        TrainingSession.trainer_id == current_user.id,
        TrainingSession.session_date == payload.session_date,
        TrainingSession.is_cancelled == False,
        TrainingSession.start_time < payload.end_time,
        TrainingSession.end_time > payload.start_time,
    ).first()
    if overlap:
        raise HTTPException(status_code=409, detail="У тренера уже есть запись в это время")

    session = TrainingSession(
        trainer_id=current_user.id,
        session_date=payload.session_date,
        start_time=payload.start_time,
        end_time=payload.end_time,
        gym_zone_id=payload.gym_zone_id,
        is_cancelled=False,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return TrainingSessionResponse(
        id=session.id,
        session_date=session.session_date,
        start_time=session.start_time,
        end_time=session.end_time,
        gym_zone=session.gym_zone,
        trainer=session.trainer,
        participants_count=0,
        participants=[],
    )


@router.get("", response_model=List[TrainingSessionResponse])
async def list_training_sessions(
    session_date: date = Query(..., description="Дата (YYYY-MM-DD)"),
    gym_zone_id: Optional[int] = Query(None, description="ID зала (опционально)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Список записей на дату. Клиент видит все, тренер — только свои."""
    q = db.query(TrainingSession).filter(
        TrainingSession.session_date == session_date,
        TrainingSession.is_cancelled == False,
    )
    if gym_zone_id:
        q = q.filter(TrainingSession.gym_zone_id == gym_zone_id)

    if current_user.role == UserRole.TRAINER:
        q = q.filter(TrainingSession.trainer_id == current_user.id)

    sessions = q.order_by(TrainingSession.start_time.asc()).all()

    # Предзагрузка участников
    session_ids = [s.id for s in sessions]
    parts = []
    if session_ids:
        parts = db.query(TrainingSessionParticipant).filter(TrainingSessionParticipant.session_id.in_(session_ids)).all()

    parts_by_session = {}
    for p in parts:
        parts_by_session.setdefault(p.session_id, []).append(p)

    resp: List[TrainingSessionResponse] = []
    for s in sessions:
        plist = parts_by_session.get(s.id, [])
        participants_count = len(plist)

        if current_user.role == UserRole.TRAINER and s.trainer_id == current_user.id:
            participants = [p.client for p in plist]
            resp.append(TrainingSessionResponse(
                id=s.id,
                session_date=s.session_date,
                start_time=s.start_time,
                end_time=s.end_time,
                gym_zone=s.gym_zone,
                trainer=s.trainer,
                participants_count=participants_count,
                participants=participants,
            ))
        elif current_user.role == UserRole.CLIENT:
            is_signed = any(p.client_id == current_user.id for p in plist)
            resp.append(TrainingSessionResponse(
                id=s.id,
                session_date=s.session_date,
                start_time=s.start_time,
                end_time=s.end_time,
                gym_zone=s.gym_zone,
                trainer=s.trainer,
                participants_count=participants_count,
                is_signed=is_signed,
            ))
        else:
            resp.append(TrainingSessionResponse(
                id=s.id,
                session_date=s.session_date,
                start_time=s.start_time,
                end_time=s.end_time,
                gym_zone=s.gym_zone,
                trainer=s.trainer,
                participants_count=participants_count,
            ))

    return resp


@router.post("/{session_id}/signup", status_code=status.HTTP_201_CREATED)
async def signup_for_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.CLIENT))
):
    """Клиент записывается на запись расписания"""
    session = db.query(TrainingSession).filter(
        TrainingSession.id == session_id,
        TrainingSession.is_cancelled == False
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    # Проверка дубля
    exists = db.query(TrainingSessionParticipant).filter(
        TrainingSessionParticipant.session_id == session_id,
        TrainingSessionParticipant.client_id == current_user.id
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail="Вы уже записаны на эту тренировку")

    # Ограничение по вместимости зала (если задано)
    if session.gym_zone_id:
        zone = db.query(GymZone).filter(GymZone.id == session.gym_zone_id).first()
        if zone and zone.capacity and zone.capacity > 0:
            cnt = db.query(TrainingSessionParticipant).filter(
                TrainingSessionParticipant.session_id == session_id
            ).count()
            if cnt >= zone.capacity:
                raise HTTPException(status_code=409, detail="В этом зале больше нет мест")

    part = TrainingSessionParticipant(session_id=session_id, client_id=current_user.id)
    db.add(part)
    db.commit()

    return {"status": "ok"}


