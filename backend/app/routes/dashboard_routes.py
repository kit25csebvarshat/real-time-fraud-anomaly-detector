from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List

from app.database import get_db
from app.models import OAuthApp, RiskScan, AuditLog
from app.schemas import DashboardStatsResponse, AuditLogResponse
from app.services.permission_engine import get_permission_info

router = APIRouter(prefix="/dashboard", tags=["Dashboard Intelligence"])

@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(db: Session = Depends(get_db)):
    apps = db.query(OAuthApp).all()
    total_apps = len(apps)

    low_cnt = 0
    med_cnt = 0
    high_cnt = 0
    crit_cnt = 0
    review_cnt = 0

    top_risk_list = []
    recent_scans_list = []
    perm_categories: Dict[str, int] = {}

    for app in apps:
        if app.status == "REVIEW":
            review_cnt += 1
        
        latest_scan = db.query(RiskScan).filter(RiskScan.app_id == app.id).order_by(RiskScan.scanned_at.desc()).first()
        score = latest_scan.final_score if latest_scan else 0.0
        level = latest_scan.risk_level if latest_scan else "LOW"

        if level == "LOW":
            low_cnt += 1
        elif level == "MEDIUM":
            med_cnt += 1
        elif level == "HIGH":
            high_cnt += 1
        elif level == "CRITICAL":
            crit_cnt += 1

        top_risk_list.append({
            "id": app.id,
            "name": app.name,
            "developer": app.developer,
            "category": app.category,
            "status": app.status,
            "risk_score": score,
            "risk_level": level,
            "requested_permissions_count": len(app.requested_permissions)
        })

        if latest_scan:
            recent_scans_list.append({
                "app_id": app.id,
                "app_name": app.name,
                "final_score": latest_scan.final_score,
                "risk_level": latest_scan.risk_level,
                "scanned_at": latest_scan.scanned_at.isoformat()
            })

        for p in app.requested_permissions:
            cat = get_permission_info(p)["category"]
            perm_categories[cat] = perm_categories.get(cat, 0) + 1

    # Sort top risk applications
    top_risk_list.sort(key=lambda x: x["risk_score"], reverse=True)
    top_risk_apps = top_risk_list[:5]

    # Sort recent scans
    recent_scans_list.sort(key=lambda x: x["scanned_at"], reverse=True)
    recent_scans = recent_scans_list[:5]

    # Fetch recent audit actions
    recent_audit_logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(10).all()
    recent_actions = [AuditLogResponse.from_orm(log) for log in recent_audit_logs]

    risk_dist = [
        {"name": "Low Risk", "value": low_cnt, "color": "#10B981"},
        {"name": "Medium Risk", "value": med_cnt, "color": "#F59E0B"},
        {"name": "High Risk", "value": high_cnt, "color": "#EF4444"},
        {"name": "Critical Risk", "value": crit_cnt, "color": "#8B5CF6"}
    ]

    category_dist = [
        {"category": k.capitalize(), "count": v} for k, v in perm_categories.items()
    ]

    return DashboardStatsResponse(
        total_apps=total_apps,
        low_risk_count=low_cnt,
        medium_risk_count=med_cnt,
        high_risk_count=high_cnt,
        critical_risk_count=crit_cnt,
        apps_requiring_review=review_cnt,
        risk_distribution=risk_dist,
        top_risk_apps=top_risk_apps,
        recent_scans=recent_scans,
        recent_actions=recent_actions,
        permission_category_distribution=category_dist
    )
