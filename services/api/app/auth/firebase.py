import json
import os
from typing import Optional

import firebase_admin
from firebase_admin import auth, credentials
from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import User

_firebase_initialized = False


def init_firebase() -> bool:
    global _firebase_initialized
    if _firebase_initialized:
        return True
    raw = settings.firebase_service_account_json.strip()
    if not raw:
        return False
    try:
        if raw.startswith("{"):
            cred = credentials.Certificate(json.loads(raw))
        else:
            cred = credentials.Certificate(raw)
        firebase_admin.initialize_app(cred)
        _firebase_initialized = True
        return True
    except Exception:
        return False


def verify_token_optional(
    db: Session, authorization: Optional[str]
) -> Optional[User]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    if not init_firebase():
        return None

    token = authorization.split(" ", 1)[1]
    try:
        decoded = auth.verify_id_token(token)
    except Exception:
        return None

    uid = decoded.get("uid")
    if not uid:
        return None

    user = db.query(User).filter(User.firebase_uid == uid).first()
    if user:
        if decoded.get("email"):
            user.email = decoded.get("email")
        if decoded.get("name"):
            user.display_name = decoded.get("name")
        if decoded.get("picture"):
            user.photo_url = decoded.get("picture")
        db.commit()
        return user

    user = User(
        firebase_uid=uid,
        email=decoded.get("email"),
        display_name=decoded.get("name"),
        photo_url=decoded.get("picture"),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
