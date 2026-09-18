from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import AuditLog
from app.schemas import AuditLogResponse

router = APIRouter(prefix="/audit-logs", tags=["Audit Trail"])

@router.get("", response_model=List[AuditLogResponse])
def get_audit_logs(
    action: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db)
):
    query = db.query(AuditLog)
    if action:
        query = query.filter(AuditLog.action == action)
    if search:
        query = query.filter(AuditLog.app_name.ilike(f"%{search}%") | AuditLog.reason.ilike(f"%{search}%"))

    logs = query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
    return [AuditLogResponse.from_orm(l) for l in logs]
