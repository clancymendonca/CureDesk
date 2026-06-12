import logging
from typing import Optional

from fastapi import APIRouter, Depends, Header, Request
from groq import Groq
from sqlalchemy.orm import Session

from app.auth.firebase import verify_token_optional
from app.chat.context import (
    CRISIS_REPLY,
    build_offline_reply,
    build_system_prompt,
    is_crisis_message,
)
from app.config import settings
from app.db.models import get_db
from app.limiter import limiter
from app.schemas import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["chat"])

SYSTEM_PROMPT = """You are CureDesk, a helpful health information assistant.
IMPORTANT RULES:
- You are NOT a doctor and cannot diagnose conditions.
- Never prescribe medications or dosages.
- Always recommend consulting a qualified healthcare professional for medical decisions.
- Provide general educational information only.
- If symptoms seem serious, urge the user to seek emergency care immediately.
- Only state disease or drug facts that appear in the provided knowledge base context; otherwise say you are unsure."""


@router.post("/chat", response_model=ChatResponse)
@limiter.limit("20/hour")
async def chat(
    request: Request,
    body: ChatRequest,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(default=None),
):
    verify_token_optional(db, authorization)

    if is_crisis_message(body.message):
        return ChatResponse(reply=CRISIS_REPLY)

    if not settings.groq_api_key:
        # No LLM configured: answer directly from the knowledge base instead
        # of failing, so chat stays useful in degraded mode.
        return ChatResponse(reply=build_offline_reply(db, body.message))

    system = build_system_prompt(db, body.message, SYSTEM_PROMPT)
    client = Groq(api_key=settings.groq_api_key)
    messages = [{"role": "system", "content": system}]
    # Only forward user turns from client-supplied history: forged
    # "assistant" messages could otherwise steer the model past its rules.
    for msg in body.history[-10:]:
        if msg.role == "user":
            messages.append({"role": "user", "content": msg.content})
    messages.append({"role": "user", "content": body.message})

    try:
        completion = client.chat.completions.create(
            model=settings.groq_model,
            messages=messages,
            max_tokens=1024,
        )
        reply = completion.choices[0].message.content or ""
    except Exception:
        # LLM outage shouldn't take chat down — answer from the knowledge base.
        logger.exception("Groq completion failed; falling back to offline reply")
        return ChatResponse(reply=build_offline_reply(db, body.message))
    return ChatResponse(reply=reply)
