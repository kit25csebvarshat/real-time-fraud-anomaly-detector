from sqlalchemy.orm import Session
from datetime import datetime
from app.models import AuditLog

def log_audit_event(
    db: Session,
    user_email: str,
    app_name: str,
    action: str,
    reason: str,
    app_id: int = None,
    previous_risk: float = None,
    current_risk: float = None,
    previous_status: str = None,
    current_status: str = None
) -> AuditLog:
    log_entry = AuditLog(
        timestamp=datetime.utcnow(),
        user_email=user_email,
        app_id=app_id,
        app_name=app_name,
        action=action,
        previous_risk=previous_risk,
        current_risk=current_risk,
        previous_status=previous_status,
        current_status=current_status,
        reason=reason
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry
