from typing import List, Dict, Any

# Taxonomy mapping permission string -> (sensitivity, category, description)
PERMISSION_TAXONOMY: Dict[str, Dict[str, str]] = {
    # LOW
    "profile.read": {"sensitivity": "LOW", "category": "profile", "description": "View user's basic profile details (name, avatar)"},
    "basic_identity.read": {"sensitivity": "LOW", "category": "profile", "description": "View basic account identity information"},
    "timezone.read": {"sensitivity": "LOW", "category": "profile", "description": "Read user's primary timezone and locale settings"},
    "user.info": {"sensitivity": "LOW", "category": "profile", "description": "View public account information"},

    # MEDIUM
    "calendar.read": {"sensitivity": "MEDIUM", "category": "calendar", "description": "Read events, schedules, and meeting details"},
    "contacts.read": {"sensitivity": "MEDIUM", "category": "contacts", "description": "Read contact lists and address books"},
    "drive.read": {"sensitivity": "MEDIUM", "category": "drive", "description": "Read files, folders, and documents stored in cloud drive"},
    "files.read": {"sensitivity": "MEDIUM", "category": "drive", "description": "Access document metadata and contents"},

    # HIGH
    "gmail.read": {"sensitivity": "HIGH", "category": "email", "description": "Read inbox emails, attachments, and thread histories"},
    "mail.read": {"sensitivity": "HIGH", "category": "email", "description": "Read mailbox messages"},
    "drive.write": {"sensitivity": "HIGH", "category": "drive", "description": "Create, edit, upload, or delete cloud files"},
    "files.write": {"sensitivity": "HIGH", "category": "drive", "description": "Modify document contents and storage"},
    "contacts.write": {"sensitivity": "HIGH", "category": "contacts", "description": "Create, edit, or delete contact records"},
    "calendar.write": {"sensitivity": "HIGH", "category": "calendar", "description": "Create, modify, or delete calendar meetings and invites"},

    # CRITICAL
    "gmail.send": {"sensitivity": "CRITICAL", "category": "email", "description": "Draft and send emails as the authenticated user"},
    "mail.send": {"sensitivity": "CRITICAL", "category": "email", "description": "Send emails on behalf of the user"},
    "admin.access": {"sensitivity": "CRITICAL", "category": "admin", "description": "Full administrative access to organizational settings and users"},
    "account.modify": {"sensitivity": "CRITICAL", "category": "admin", "description": "Modify account credentials and security settings"},
    "user.impersonation": {"sensitivity": "CRITICAL", "category": "admin", "description": "Impersonate any user account across the domain"},
    "directory.write": {"sensitivity": "CRITICAL", "category": "admin", "description": "Modify corporate employee directory entries"}
}

def get_permission_info(perm: str) -> Dict[str, str]:
    if perm in PERMISSION_TAXONOMY:
        return PERMISSION_TAXONOMY[perm]
    
    # Generic fallback logic for unknown permissions
    if "admin" in perm or "impersonat" in perm or "send" in perm:
        return {"sensitivity": "CRITICAL", "category": "admin", "description": f"Custom scope ({perm}) with high risk keywords"}
    elif "write" in perm or "modify" in perm or "mail" in perm or "gmail" in perm:
        return {"sensitivity": "HIGH", "category": "general", "description": f"Custom scope ({perm}) with write or email access"}
    elif "read" in perm:
        return {"sensitivity": "MEDIUM", "category": "general", "description": f"Custom scope ({perm}) with read access"}
    else:
        return {"sensitivity": "LOW", "category": "general", "description": f"Custom scope ({perm})"}

def analyze_suspicious_combinations(permissions: List[str]) -> List[Dict[str, Any]]:
    perm_set = set(permissions)
    combos = []

    # 1. Email Read + Email Send
    has_email_read = "gmail.read" in perm_set or "mail.read" in perm_set
    has_email_send = "gmail.send" in perm_set or "mail.send" in perm_set
    if has_email_read and has_email_send:
        combos.append({
            "combination": [p for p in ["gmail.read", "mail.read", "gmail.send", "mail.send"] if p in perm_set],
            "title": "Email Data Access & Impersonated Sending Risk",
            "severity": "CRITICAL",
            "explanation": "Allows the application to both read sensitive email conversations AND send emails as the user, creating a severe internal phishing and data exfiltration vector."
        })

    # 2. Drive Read + Drive Write
    has_drive_read = "drive.read" in perm_set or "files.read" in perm_set
    has_drive_write = "drive.write" in perm_set or "files.write" in perm_set
    if has_drive_read and has_drive_write:
        combos.append({
            "combination": [p for p in ["drive.read", "files.read", "drive.write", "files.write"] if p in perm_set],
            "title": "Full Cloud Storage Control",
            "severity": "HIGH",
            "explanation": "Grants uninhibited read, write, modification, and deletion access to all cloud documents (ransomware or data corruption risk)."
        })

    # 3. Broad Multi-Domain Sensitive Access
    has_contacts_read = "contacts.read" in perm_set
    has_calendar_read = "calendar.read" in perm_set
    if has_email_read and has_drive_read and has_contacts_read:
        combos.append({
            "combination": [p for p in ["gmail.read", "mail.read", "drive.read", "files.read", "contacts.read"] if p in perm_set],
            "title": "Broad Cross-Domain Data Access",
            "severity": "CRITICAL",
            "explanation": "Requests comprehensive read access across emails, documents, and corporate contact lists simultaneously."
        })

    # 4. Admin Access + Any Write/Send Permission
    has_admin = "admin.access" in perm_set or "account.modify" in perm_set
    has_any_write = has_drive_write or has_email_send or "contacts.write" in perm_set or "calendar.write" in perm_set
    if has_admin and has_any_write:
        combos.append({
            "combination": [p for p in permissions if "admin" in p or "write" in p or "send" in p],
            "title": "Privileged Application Over-Authorization",
            "severity": "CRITICAL",
            "explanation": "Combines administrative domain authority with active write/send capabilities."
        })

    # 5. User Impersonation Risk
    if "user.impersonation" in perm_set:
        combos.append({
            "combination": ["user.impersonation"],
            "title": "Domain Identity Takeover Capability",
            "severity": "CRITICAL",
            "explanation": "Allows performing arbitrary actions while spoofing employee identities."
        })

    return combos
