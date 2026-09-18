from typing import List, Dict, Any, Tuple
from app.services.permission_engine import get_permission_info

def analyze_purpose_permission_fit(
    declared_purpose: str, category: str, requested_permissions: List[str]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Analyzes whether requested permissions are consistent with declared application purpose.
    Returns:
      - breakdown: list of all permissions with relevance tag (RELEVANT, POTENTIALLY_EXCESSIVE, HIGH_RISK_MISMATCH)
      - mismatches: list of flagged mismatches with detailed natural language reasons
    """
    purpose_lower = (declared_purpose + " " + category).lower()
    
    # Identify declared primary domain capabilities based on keywords
    is_doc_pdf = any(k in purpose_lower for k in ["pdf", "document", "file", "org", "convert", "folder"])
    is_calendar = any(k in purpose_lower for k in ["calendar", "schedule", "meeting", "event", "time", "invite"])
    is_email = any(k in purpose_lower for k in ["email", "mail", "inbox", "outbox", "copilot", "draft"])
    is_backup = any(k in purpose_lower for k in ["backup", "vault", "archive", "storage", "sync"])
    is_transcribe = any(k in purpose_lower for k in ["transcrib", "speech", "audio", "notes", "recording"])
    is_crm = any(k in purpose_lower for k in ["crm", "customer", "contacts", "leads", "sales"])
    is_signing = any(k in purpose_lower for k in ["sign", "e-sign", "signature", "contract"])
    is_social = any(k in purpose_lower for k in ["social", "post", "tweet", "share", "media"])

    breakdown = []
    mismatches = []

    for perm in requested_permissions:
        info = get_permission_info(perm)
        sensitivity = info["sensitivity"]
        perm_cat = info["category"]
        desc = info["description"]

        relevance = "RELEVANT"
        reason = ""

        # Profile/Identity is universally relevant for basic auth
        if perm_cat == "profile":
            relevance = "RELEVANT"
            reason = "Standard scope required for user authentication."

        # Document/File Converter domain
        elif is_doc_pdf and not (is_email or is_calendar or is_crm):
            if perm in ["drive.read", "files.read"]:
                relevance = "RELEVANT"
                reason = "Required to read source documents for conversion."
            elif perm in ["drive.write", "files.write"]:
                relevance = "RELEVANT"
                reason = "Required to save converted PDF documents back to cloud storage."
            elif perm in ["contacts.read", "calendar.read"]:
                relevance = "POTENTIALLY_EXCESSIVE"
                reason = f"Access to {perm_cat} is not typically required for document conversion workflows."
                mismatches.append({"permission": perm, "classification": relevance, "reason": reason})
            elif perm in ["gmail.read", "mail.read", "gmail.send", "mail.send", "admin.access", "user.impersonation"]:
                relevance = "HIGH_RISK_MISMATCH"
                reason = f"High-risk permission ({perm}) requested by a document converter app with no declared email or administration purpose."
                mismatches.append({"permission": perm, "classification": relevance, "reason": reason})

        # Calendar Scheduling domain
        elif is_calendar and not (is_email or is_doc_pdf):
            if perm in ["calendar.read", "calendar.write"]:
                relevance = "RELEVANT"
                reason = "Core permission required for calendar meeting management."
            elif perm in ["contacts.read"]:
                relevance = "RELEVANT"
                reason = "Allows looking up meeting attendees in contacts."
            elif perm in ["drive.read", "files.read"]:
                relevance = "POTENTIALLY_EXCESSIVE"
                reason = "Reading cloud storage files is beyond standard calendar scheduling needs."
                mismatches.append({"permission": perm, "classification": relevance, "reason": reason})
            elif perm in ["drive.write", "gmail.send", "mail.send", "gmail.read", "admin.access"]:
                relevance = "HIGH_RISK_MISMATCH"
                reason = f"Permission {perm} is unrelated to calendar scheduling and exposes sensitive actions."
                mismatches.append({"permission": perm, "classification": relevance, "reason": reason})

        # Meeting Transcription domain
        elif is_transcribe:
            if perm in ["calendar.read"]:
                relevance = "RELEVANT"
                reason = "Required to discover upcoming meeting sessions for transcription."
            elif perm in ["drive.write"]:
                relevance = "RELEVANT"
                reason = "Required to save meeting transcripts to drive."
            elif perm in ["gmail.send", "mail.send"]:
                relevance = "HIGH_RISK_MISMATCH"
                reason = "Sending emails directly is not required for transcription apps; summary links can be shared via drive."
                mismatches.append({"permission": perm, "classification": relevance, "reason": reason})
            elif perm in ["gmail.read", "contacts.write"]:
                relevance = "POTENTIALLY_EXCESSIVE"
                reason = f"{perm} is excessive for meeting note generation."
                mismatches.append({"permission": perm, "classification": relevance, "reason": reason})

        # General check for unaligned high/critical permissions
        else:
            if sensitivity in ["HIGH", "CRITICAL"]:
                if perm_cat == "email" and not is_email:
                    relevance = "HIGH_RISK_MISMATCH"
                    reason = f"App declared purpose does not justify sensitive email permission ({perm})."
                    mismatches.append({"permission": perm, "classification": relevance, "reason": reason})
                elif perm_cat == "admin":
                    relevance = "HIGH_RISK_MISMATCH"
                    reason = "Administrative privilege requested by standard user application."
                    mismatches.append({"permission": perm, "classification": relevance, "reason": reason})
                elif perm_cat == "drive" and not (is_doc_pdf or is_backup or is_signing):
                    relevance = "POTENTIALLY_EXCESSIVE"
                    reason = f"Cloud drive access ({perm}) appears excessive for the declared purpose."
                    mismatches.append({"permission": perm, "classification": relevance, "reason": reason})

        breakdown.append({
            "permission": perm,
            "category": perm_cat,
            "sensitivity": sensitivity,
            "purpose_relevance": relevance,
            "description": desc
        })

    return breakdown, mismatches
