import json
import logging
from typing import Optional

import firebase_admin
from fastapi import HTTPException
from firebase_admin import auth, credentials
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import User

logger = logging.getLogger(__name__)

_firebase_initialized = False
_firebase_init_failed = False


def init_firebase() -> bool:
    global _firebase_initialized, _firebase_init_failed
    if _firebase_initialized:
        return True
    if _firebase_init_failed:
        return False
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
        _firebase_init_failed = True
        logger.exception(
            "Firebase initialization failed; check FIREBASE_SERVICE_ACCOUNT_JSON. "
            "All requests will be treated as anonymous."
        )
        return False


def _unauthenticated(message: str) -> HTTPException:
    return HTTPException(
        status_code=401,
        detail={"error": {"code": "UNAUTHENTICATED", "message": message}},
    )


def verify_token_optional(
    db: Session, authorization: Optional[str]
) -> Optional[User]:
    """Resolve the request's Firebase user, if any.

    - No Authorization header -> anonymous (returns None).
    - Header present but token invalid/expired -> 401, so clients know to
      refresh instead of silently losing the link to their account.
    - Firebase not configured -> anonymous (logged once at init).
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    if not init_firebase():
        return None

    token = authorization.split(" ", 1)[1]
    try:
        decoded = auth.verify_id_token(token)
    except Exception:
        raise _unauthenticated("Invalid or expired authentication token")

    uid = decoded.get("uid")
    if not uid:
        raise _unauthenticated("Invalid authentication token")

    user = db.query(User).filter(User.firebase_uid == uid).first()
    if user:
        changed = False
        for attr, claim in (
            ("email", "email"),
            ("display_name", "name"),
            ("photo_url", "picture"),
        ):
            value = decoded.get(claim)
            if value and getattr(user, attr) != value:
                setattr(user, attr, value)
                changed = True
        if changed:
            db.commit()
        return user

    user = User(
        firebase_uid=uid,
        email=decoded.get("email"),
        display_name=decoded.get("name"),
        photo_url=decoded.get("picture"),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        # Concurrent first requests can race on the unique firebase_uid index.
        db.rollback()
        user = db.query(User).filter(User.firebase_uid == uid).first()
        if user is None:
            raise
        return user
    db.refresh(user)
    return user


def verify_token_required(db: Session, authorization: Optional[str]) -> User:
    """Like verify_token_optional, but missing credentials are also a 401."""
    user = verify_token_optional(db, authorization)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail={"error": {"code": "UNAUTHORIZED", "message": "Sign in required"}},
        )
    return user
