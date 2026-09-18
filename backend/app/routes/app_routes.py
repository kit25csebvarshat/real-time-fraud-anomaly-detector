from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models import OAuthApp, RiskScan, User
from app.schemas import (
    AppCreate, AppResponse, RiskScanResponse, ActionRequest,
    WhatIfSimulationRequest, WhatIfSimulationResponse
)
from app.auth import get_current_user
from app.services.risk_engine import calculate_hybrid_risk_assessment
from app.services.explanation_engine import generate_explainable_narrative
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/apps", tags=["OAuth Applications"])

def build_app_response(app: OAuthApp, db: Session) -> AppResponse:
    latest_scan = db.query(RiskScan).filter(RiskScan.app_id == app.id).order_by(RiskScan.scanned_at.desc()).first()
    res = AppResponse.from_orm(app)
    if latest_scan:
        res.current_risk_score = latest_scan.final_score
        res.current_risk_level = latest_scan.risk_level
    else:
        res.current_risk_score = None
        res.current_risk_level = None
    return res

@router.get("", response_model=List[AppResponse])
def list_apps(
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(OAuthApp)
    if status_filter:
        query = query.filter(OAuthApp.status == status_filter.upper())
    if search:
        query = query.filter(OAuthApp.name.ilike(f"%{search}%") | OAuthApp.developer.ilike(f"%{search}%"))
    
    apps = query.order_by(OAuthApp.created_at.desc()).all()
    return [build_app_response(app, db) for app in apps]

@router.post("", response_model=AppResponse, status_code=status.HTTP_201_CREATED)
def create_app(
    app_in: AppCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    app = OAuthApp(
        name=app_in.name,
        developer=app_in.developer,
        developer_verified=app_in.developer_verified,
        declared_purpose=app_in.declared_purpose,
        app_age_days=app_in.app_age_days,
        user_count=app_in.user_count,
        category=app_in.category,
        requested_permissions=app_in.requested_permissions,
        status="ACTIVE"
    )
    db.add(app)
    db.commit()
    db.refresh(app)

    # Automatically run initial scan
    assessment = calculate_hybrid_risk_assessment(
        name=app.name,
        declared_purpose=app.declared_purpose,
        category=app.category,
        developer=app.developer,
        developer_verified=app.developer_verified,
        app_age_days=app.app_age_days,
        user_count=app.user_count,
        requested_permissions=app.requested_permissions
    )

    explanation = generate_explainable_narrative(
        app_name=app.name,
        declared_purpose=app.declared_purpose,
        final_score=assessment["final_score"],
        risk_level=assessment["risk_level"],
        major_risk_factors=assessment["major_risk_factors"],
        purpose_mismatches=assessment["purpose_mismatches"],
        suspicious_combinations=assessment["suspicious_combinations"],
        requested_permissions=app.requested_permissions
    )

    scan = RiskScan(
        app_id=app.id,
        rule_score=assessment["rule_score"],
        ml_score=assessment["ml_score"],
        final_score=assessment["final_score"],
        risk_level=assessment["risk_level"],
        major_risk_factors=assessment["major_risk_factors"],
        purpose_mismatches=assessment["purpose_mismatches"],
        suspicious_combinations=assessment["suspicious_combinations"],
        potential_impact=explanation["potential_impact"],
        recommended_action=explanation["recommended_action"]
    )
    db.add(scan)
    app.last_scanned = datetime.utcnow()
    db.commit()

    user_email = current_user.email if current_user else "admin@oauthguard.io"
    log_audit_event(
        db=db,
        user_email=user_email,
        app_id=app.id,
        app_name=app.name,
        action="ADD_APP",
        current_risk=assessment["final_score"],
        current_status="ACTIVE",
        reason=f"Registered new OAuth application with {len(app.requested_permissions)} requested permissions."
    )

    return build_app_response(app, db)

@router.get("/{app_id}", response_model=AppResponse)
def get_app(app_id: int, db: Session = Depends(get_db)):
    app = db.query(OAuthApp).filter(OAuthApp.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="OAuth application not found")
    return build_app_response(app, db)

@router.post("/{app_id}/scan", response_model=RiskScanResponse)
def run_scan(app_id: int, db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_current_user)):
    app = db.query(OAuthApp).filter(OAuthApp.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="OAuth application not found")

    assessment = calculate_hybrid_risk_assessment(
        name=app.name,
        declared_purpose=app.declared_purpose,
        category=app.category,
        developer=app.developer,
        developer_verified=app.developer_verified,
        app_age_days=app.app_age_days,
        user_count=app.user_count,
        requested_permissions=app.requested_permissions
    )

    explanation = generate_explainable_narrative(
        app_name=app.name,
        declared_purpose=app.declared_purpose,
        final_score=assessment["final_score"],
        risk_level=assessment["risk_level"],
        major_risk_factors=assessment["major_risk_factors"],
        purpose_mismatches=assessment["purpose_mismatches"],
        suspicious_combinations=assessment["suspicious_combinations"],
        requested_permissions=app.requested_permissions
    )

    prev_scan = db.query(RiskScan).filter(RiskScan.app_id == app.id).order_by(RiskScan.scanned_at.desc()).first()
    prev_risk = prev_scan.final_score if prev_scan else None

    scan = RiskScan(
        app_id=app.id,
        rule_score=assessment["rule_score"],
        ml_score=assessment["ml_score"],
        final_score=assessment["final_score"],
        risk_level=assessment["risk_level"],
        major_risk_factors=assessment["major_risk_factors"],
        purpose_mismatches=assessment["purpose_mismatches"],
        suspicious_combinations=assessment["suspicious_combinations"],
        potential_impact=explanation["potential_impact"],
        recommended_action=explanation["recommended_action"]
    )
    db.add(scan)
    app.last_scanned = datetime.utcnow()
    db.commit()
    db.refresh(scan)

    user_email = current_user.email if current_user else "admin@oauthguard.io"
    log_audit_event(
        db=db,
        user_email=user_email,
        app_id=app.id,
        app_name=app.name,
        action="RESCAN",
        previous_risk=prev_risk,
        current_risk=assessment["final_score"],
        previous_status=app.status,
        current_status=app.status,
        reason="Triggered manual permission risk rescan."
    )

    res = RiskScanResponse.from_orm(scan)
    res.permissions_breakdown = assessment["permissions_breakdown"]
    return res

@router.get("/{app_id}/risk", response_model=RiskScanResponse)
def get_latest_risk(app_id: int, db: Session = Depends(get_db)):
    app = db.query(OAuthApp).filter(OAuthApp.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="OAuth application not found")

    scan = db.query(RiskScan).filter(RiskScan.app_id == app_id).order_by(RiskScan.scanned_at.desc()).first()
    if not scan:
        # Run scan if none exists
        assessment = calculate_hybrid_risk_assessment(
            name=app.name,
            declared_purpose=app.declared_purpose,
            category=app.category,
            developer=app.developer,
            developer_verified=app.developer_verified,
            app_age_days=app.app_age_days,
            user_count=app.user_count,
            requested_permissions=app.requested_permissions
        )
        explanation = generate_explainable_narrative(
            app_name=app.name,
            declared_purpose=app.declared_purpose,
            final_score=assessment["final_score"],
            risk_level=assessment["risk_level"],
            major_risk_factors=assessment["major_risk_factors"],
            purpose_mismatches=assessment["purpose_mismatches"],
            suspicious_combinations=assessment["suspicious_combinations"],
            requested_permissions=app.requested_permissions
        )
        scan = RiskScan(
            app_id=app.id,
            rule_score=assessment["rule_score"],
            ml_score=assessment["ml_score"],
            final_score=assessment["final_score"],
            risk_level=assessment["risk_level"],
            major_risk_factors=assessment["major_risk_factors"],
            purpose_mismatches=assessment["purpose_mismatches"],
            suspicious_combinations=assessment["suspicious_combinations"],
            potential_impact=explanation["potential_impact"],
            recommended_action=explanation["recommended_action"]
        )
        db.add(scan)
        db.commit()
        db.refresh(scan)
    
    # Calculate fresh breakdown
    assessment = calculate_hybrid_risk_assessment(
        name=app.name,
        declared_purpose=app.declared_purpose,
        category=app.category,
        developer=app.developer,
        developer_verified=app.developer_verified,
        app_age_days=app.app_age_days,
        user_count=app.user_count,
        requested_permissions=app.requested_permissions
    )

    res = RiskScanResponse.from_orm(scan)
    res.permissions_breakdown = assessment["permissions_breakdown"]
    return res

@router.get("/{app_id}/explanation")
def get_app_explanation(app_id: int, db: Session = Depends(get_db)):
    app = db.query(OAuthApp).filter(OAuthApp.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="OAuth application not found")

    scan = db.query(RiskScan).filter(RiskScan.app_id == app_id).order_by(RiskScan.scanned_at.desc()).first()
    if not scan:
        raise HTTPException(status_code=404, detail="No risk scan available for this app")

    return {
        "app_name": app.name,
        "risk_score": scan.final_score,
        "risk_level": scan.risk_level,
        "major_risk_factors": scan.major_risk_factors,
        "potential_impact": scan.potential_impact,
        "recommended_action": scan.recommended_action,
        "purpose_mismatches": scan.purpose_mismatches,
        "suspicious_combinations": scan.suspicious_combinations
    }

@router.post("/{app_id}/trust", response_model=AppResponse)
def mark_trusted(
    app_id: int,
    action_in: ActionRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    app = db.query(OAuthApp).filter(OAuthApp.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="OAuth application not found")

    prev_status = app.status
    app.status = "TRUSTED"
    db.commit()

    scan = db.query(RiskScan).filter(RiskScan.app_id == app.id).order_by(RiskScan.scanned_at.desc()).first()
    risk_val = scan.final_score if scan else None

    user_email = current_user.email if current_user else "admin@oauthguard.io"
    log_audit_event(
        db=db,
        user_email=user_email,
        app_id=app.id,
        app_name=app.name,
        action="MARK_TRUSTED",
        previous_risk=risk_val,
        current_risk=risk_val,
        previous_status=prev_status,
        current_status="TRUSTED",
        reason=action_in.reason or "Administrator marked application as trusted."
    )

    return build_app_response(app, db)

@router.post("/{app_id}/review", response_model=AppResponse)
def mark_review(
    app_id: int,
    action_in: ActionRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    app = db.query(OAuthApp).filter(OAuthApp.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="OAuth application not found")

    prev_status = app.status
    app.status = "REVIEW"
    db.commit()

    scan = db.query(RiskScan).filter(RiskScan.app_id == app.id).order_by(RiskScan.scanned_at.desc()).first()
    risk_val = scan.final_score if scan else None

    user_email = current_user.email if current_user else "admin@oauthguard.io"
    log_audit_event(
        db=db,
        user_email=user_email,
        app_id=app.id,
        app_name=app.name,
        action="MARK_REVIEW",
        previous_risk=risk_val,
        current_risk=risk_val,
        previous_status=prev_status,
        current_status="REVIEW",
        reason=action_in.reason or "Application flagged for detailed security review."
    )

    return build_app_response(app, db)

@router.post("/{app_id}/revoke", response_model=AppResponse)
def revoke_access(
    app_id: int,
    action_in: ActionRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    app = db.query(OAuthApp).filter(OAuthApp.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="OAuth application not found")

    prev_status = app.status
    app.status = "REVOKED"
    db.commit()

    scan = db.query(RiskScan).filter(RiskScan.app_id == app.id).order_by(RiskScan.scanned_at.desc()).first()
    risk_val = scan.final_score if scan else None

    user_email = current_user.email if current_user else "admin@oauthguard.io"
    log_audit_event(
        db=db,
        user_email=user_email,
        app_id=app.id,
        app_name=app.name,
        action="REVOKE_ACCESS",
        previous_risk=risk_val,
        current_risk=risk_val,
        previous_status=prev_status,
        current_status="REVOKED",
        reason=action_in.reason or "SIMULATED ACTION: Access revoked by administrator."
    )

    return build_app_response(app, db)

@router.post("/{app_id}/simulate", response_model=WhatIfSimulationResponse)
def simulate_permission_removal(
    app_id: int,
    sim_in: WhatIfSimulationRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    What-If Permission Simulator: Recalculates risk dynamically based on modified permission list.
    """
    app = db.query(OAuthApp).filter(OAuthApp.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="OAuth application not found")

    # Original Assessment
    orig_assessment = calculate_hybrid_risk_assessment(
        name=app.name,
        declared_purpose=app.declared_purpose,
        category=app.category,
        developer=app.developer,
        developer_verified=app.developer_verified,
        app_age_days=app.app_age_days,
        user_count=app.user_count,
        requested_permissions=app.requested_permissions
    )

    # Simulated Assessment on modified permission list
    new_assessment = calculate_hybrid_risk_assessment(
        name=app.name,
        declared_purpose=app.declared_purpose,
        category=app.category,
        developer=app.developer,
        developer_verified=app.developer_verified,
        app_age_days=app.app_age_days,
        user_count=app.user_count,
        requested_permissions=sim_in.permissions
    )

    new_explanation = generate_explainable_narrative(
        app_name=app.name,
        declared_purpose=app.declared_purpose,
        final_score=new_assessment["final_score"],
        risk_level=new_assessment["risk_level"],
        major_risk_factors=new_assessment["major_risk_factors"],
        purpose_mismatches=new_assessment["purpose_mismatches"],
        suspicious_combinations=new_assessment["suspicious_combinations"],
        requested_permissions=sim_in.permissions
    )

    orig_score = orig_assessment["final_score"]
    new_score = new_assessment["final_score"]
    score_delta = round(new_score - orig_score, 1)

    removed_perms = list(set(app.requested_permissions) - set(sim_in.permissions))

    factor_changes = []
    if score_delta < 0:
        factor_changes.append(f"Risk reduced by {abs(score_delta)} points by removing {len(removed_perms)} permission scope(s).")
    elif score_delta > 0:
        factor_changes.append(f"Risk increased by {score_delta} points.")
    else:
        factor_changes.append("No score change observed.")

    simulated_scan_res = RiskScanResponse(
        app_id=app.id,
        rule_score=new_assessment["rule_score"],
        ml_score=new_assessment["ml_score"],
        final_score=new_assessment["final_score"],
        risk_level=new_assessment["risk_level"],
        major_risk_factors=new_assessment["major_risk_factors"],
        purpose_mismatches=new_assessment["purpose_mismatches"],
        suspicious_combinations=new_assessment["suspicious_combinations"],
        potential_impact=new_explanation["potential_impact"],
        recommended_action=new_explanation["recommended_action"],
        permissions_breakdown=new_assessment["permissions_breakdown"],
        scanned_at=datetime.utcnow()
    )

    user_email = current_user.email if current_user else "admin@oauthguard.io"
    log_audit_event(
        db=db,
        user_email=user_email,
        app_id=app.id,
        app_name=app.name,
        action="PERMISSION_SIMULATION",
        previous_risk=orig_score,
        current_risk=new_score,
        previous_status=app.status,
        current_status=app.status,
        reason=f"What-If Simulation executed: Removed permissions ({', '.join(removed_perms)}). Score changed from {orig_score} to {new_score} ({score_delta:+0.1f} pts)."
    )

    return WhatIfSimulationResponse(
        app_id=app.id,
        app_name=app.name,
        original_score=orig_score,
        new_score=new_score,
        score_delta=score_delta,
        original_level=orig_assessment["risk_level"],
        new_level=new_assessment["risk_level"],
        removed_permissions=removed_perms,
        risk_factor_changes=factor_changes,
        simulated_scan=simulated_scan_res
    )
