import sys
import os
from datetime import datetime

# Add app to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base, SessionLocal
from app.models import User, OAuthApp, RiskScan, AuditLog
from app.auth import get_password_hash
from app.services.risk_engine import calculate_hybrid_risk_assessment
from app.services.explanation_engine import generate_explainable_narrative
from app.services.audit_service import log_audit_event

def seed_database():
    print("Re-creating database tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # 1. Create Default Admin User
        admin_user = User(
            email="admin@oauthguard.io",
            hashed_password=get_password_hash("admin123"),
            full_name="Security Administrator",
            role="security_admin"
        )
        db.add(admin_user)
        db.commit()
        print("Created default admin user (admin@oauthguard.io / admin123)")

        # 2. Seed 10 Realistic Demo Applications
        demo_apps = [
            {
                "name": "DocuFlow AI",
                "developer": "DocuFlow Technologies",
                "developer_verified": False,
                "declared_purpose": "AI-powered document organization and PDF conversion platform for employees.",
                "app_age_days": 18,
                "user_count": 342,
                "category": "PDF Document Converter",
                "status": "ACTIVE",
                "requested_permissions": [
                    "profile.read",
                    "drive.read",
                    "drive.write",
                    "gmail.read",
                    "gmail.send",
                    "contacts.read",
                    "calendar.read"
                ]
            },
            {
                "name": "SyncCal Assistant",
                "developer": "SyncCal Software Inc.",
                "developer_verified": True,
                "declared_purpose": "Automated meeting scheduling and calendar sync tool for sales teams.",
                "app_age_days": 420,
                "user_count": 18500,
                "category": "Calendar Scheduling Assistant",
                "status": "TRUSTED",
                "requested_permissions": ["profile.read", "calendar.read", "calendar.write"]
            },
            {
                "name": "QuickPDF Converter",
                "developer": "Document Tools LLC",
                "developer_verified": True,
                "declared_purpose": "Utility for converting Office documents to PDF files directly in cloud storage.",
                "app_age_days": 310,
                "user_count": 6400,
                "category": "PDF Document Converter",
                "status": "ACTIVE",
                "requested_permissions": ["profile.read", "drive.read", "drive.write"]
            },
            {
                "name": "SmartEmail Copilot",
                "developer": "Copilot AI Labs",
                "developer_verified": True,
                "declared_purpose": "AI assistant that drafts email responses and summarizes inbox threads.",
                "app_age_days": 180,
                "user_count": 9200,
                "category": "AI Email Assistant",
                "status": "REVIEW",
                "requested_permissions": ["profile.read", "gmail.read", "gmail.send", "contacts.read"]
            },
            {
                "name": "VaultBackup Enterprise",
                "developer": "Vault Security Corp",
                "developer_verified": True,
                "declared_purpose": "Corporate cloud drive backup and automated archiving utility.",
                "app_age_days": 730,
                "user_count": 32000,
                "category": "Company Backup Utility",
                "status": "REVIEW",
                "requested_permissions": [
                    "profile.read",
                    "drive.read",
                    "drive.write",
                    "files.read",
                    "files.write",
                    "admin.access"
                ]
            },
            {
                "name": "TranscribeNow AI",
                "developer": "AudioAI Solutions",
                "developer_verified": False,
                "declared_purpose": "Meeting transcription and AI note-taking tool for video conferences.",
                "app_age_days": 45,
                "user_count": 1200,
                "category": "Meeting Transcription Tool",
                "status": "ACTIVE",
                "requested_permissions": ["profile.read", "calendar.read", "drive.write", "gmail.send"]
            },
            {
                "name": "OmniCRM Hub",
                "developer": "OmniSystems Global",
                "developer_verified": True,
                "declared_purpose": "B2B CRM customer relationship data sync and contact book manager.",
                "app_age_days": 520,
                "user_count": 14200,
                "category": "CRM Connector",
                "status": "TRUSTED",
                "requested_permissions": ["profile.read", "contacts.read", "contacts.write", "gmail.read"]
            },
            {
                "name": "SignExpress Pro",
                "developer": "SignExpress Inc",
                "developer_verified": False,
                "declared_purpose": "Electronic document signing and contract management platform.",
                "app_age_days": 60,
                "user_count": 890,
                "category": "Document Signing Platform",
                "status": "ACTIVE",
                "requested_permissions": ["profile.read", "drive.read", "drive.write", "gmail.send"]
            },
            {
                "name": "PostSchedule Master",
                "developer": "MediaPulse Tools",
                "developer_verified": True,
                "declared_purpose": "Social media post planning and publishing timeline assistant.",
                "app_age_days": 240,
                "user_count": 5100,
                "category": "Social Media Scheduler",
                "status": "TRUSTED",
                "requested_permissions": ["profile.read", "timezone.read", "calendar.read"]
            },
            {
                "name": "Shadow Productivity Suite",
                "developer": "Unverified Developer",
                "developer_verified": False,
                "declared_purpose": "All-in-one productivity workflow booster for remote teams.",
                "app_age_days": 12,
                "user_count": 180,
                "category": "Unknown Productivity Assistant",
                "status": "REVIEW",
                "requested_permissions": [
                    "profile.read",
                    "gmail.read",
                    "gmail.send",
                    "drive.read",
                    "drive.write",
                    "contacts.write",
                    "admin.access",
                    "user.impersonation"
                ]
            }
        ]

        print("Seeding OAuth Applications and generating security risk scans...")

        for data in demo_apps:
            app = OAuthApp(
                name=data["name"],
                developer=data["developer"],
                developer_verified=data["developer_verified"],
                declared_purpose=data["declared_purpose"],
                app_age_days=data["app_age_days"],
                user_count=data["user_count"],
                category=data["category"],
                status=data["status"],
                requested_permissions=data["requested_permissions"],
                last_scanned=datetime.utcnow()
            )
            db.add(app)
            db.commit()
            db.refresh(app)

            # Perform risk scan
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

            # Seed an audit log for initial registration
            log_audit_event(
                db=db,
                user_email="admin@oauthguard.io",
                app_id=app.id,
                app_name=app.name,
                action="INITIAL_SCAN",
                current_risk=assessment["final_score"],
                current_status=app.status,
                reason=f"Initial risk assessment computed. Risk score: {assessment['final_score']} ({assessment['risk_level']})."
            )

            print(f"  [+] {app.name:30s} -> Risk: {assessment['final_score']:5.1f} ({assessment['risk_level']})")

        print("\nDatabase seeding completed successfully!")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
