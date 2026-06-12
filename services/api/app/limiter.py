from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings

# With multiple workers/instances, in-memory storage silently resets limits;
# point RATE_LIMIT_STORAGE_URI at Redis (e.g. redis://redis:6379) in production.
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.rate_limit_storage_uri or "memory://",
)
