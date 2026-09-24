from fastapi import Request, Depends, HTTPException, status
from typing import Optional

from ..db import get_daily_usage, increment_daily_usage
from ..auth import get_current_user
from ..config import FREE_DAILY_LIMIT, AUTH_DAILY_LIMIT, AI_ENABLED

LIMIT_RESPONSE = {
    "limited": True,
    "message": (
        "You've used all your free AI credits for today. "
        "Come back tomorrow and your credits will reset! "
        "Signing in gives you 4x more daily credits."
    ),
    "tip": "Create a free account to get 200 AI requests per day instead of 50.",
}


async def ai_rate_limit(
    request: Request,
    current_user: Optional[dict] = Depends(get_current_user),
) -> Optional[dict]:
    if not AI_ENABLED:
        return current_user

    if current_user:
        key = f"user:{current_user['sub']}"
        limit = AUTH_DAILY_LIMIT
    else:
        ip = request.client.host if request.client else "unknown"
        key = f"ip:{ip}"
        limit = FREE_DAILY_LIMIT

    usage = get_daily_usage(key)
    if usage >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=LIMIT_RESPONSE,
        )

    increment_daily_usage(key)
    return current_user
