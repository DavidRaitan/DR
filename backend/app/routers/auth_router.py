from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
import re

from ..db import (
    create_user, get_user_by_email, get_user_by_username, get_user_by_id,
    update_user, user_stories, add_xp,
    save_work, list_saved_work, delete_saved_work,
    get_daily_usage,
)
from ..auth import hash_password, verify_password, create_access_token, require_user, get_current_user
from ..config import FREE_DAILY_LIMIT, AUTH_DAILY_LIMIT, AI_ENABLED

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

    def validate(self):
        self.username = self.username.strip()
        if not re.match(r"^[a-zA-Z0-9_]{3,30}$", self.username):
            raise ValueError("Username must be 3–30 chars, letters/numbers/underscore only")
        if len(self.password) < 8:
            raise ValueError("Password must be at least 8 characters")
        self.email = self.email.strip().lower()
        if "@" not in self.email:
            raise ValueError("Invalid email address")


class UpdateProfileRequest(BaseModel):
    bio: Optional[str] = None
    avatar: Optional[str] = None


class SaveWorkRequest(BaseModel):
    kind: str
    title: str = ""
    content: str


class AddXPRequest(BaseModel):
    amount: int


def _safe_user(user: dict) -> dict:
    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "bio": user["bio"],
        "avatar": user["avatar"],
        "created_at": user["created_at"],
        "level": user["level"],
        "xp": user["xp"],
    }


@router.post("/register")
def register(req: RegisterRequest):
    try:
        req.validate()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if get_user_by_email(req.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if get_user_by_username(req.username):
        raise HTTPException(status_code=400, detail="Username already taken")
    hashed = hash_password(req.password)
    user = create_user(req.username, req.email, hashed)
    token = create_access_token({"sub": str(user["id"]), "username": user["username"]})
    return {"access_token": token, "token_type": "bearer", "user": _safe_user(user)}


@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends()):
    user = get_user_by_email(form.username)
    if not user or not verify_password(form.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    token = create_access_token({"sub": str(user["id"]), "username": user["username"]})
    return {"access_token": token, "token_type": "bearer", "user": _safe_user(user)}


@router.get("/me")
def me(current_user: dict = Depends(require_user)):
    user = get_user_by_id(int(current_user["sub"]))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _safe_user(user)


@router.put("/profile")
def update_profile(req: UpdateProfileRequest, current_user: dict = Depends(require_user)):
    user = update_user(int(current_user["sub"]), bio=req.bio, avatar=req.avatar)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _safe_user(user)


@router.post("/xp")
def award_xp(req: AddXPRequest, current_user: dict = Depends(require_user)):
    if req.amount < 0 or req.amount > 100:
        raise HTTPException(status_code=400, detail="Invalid XP amount")
    result = add_xp(int(current_user["sub"]), req.amount)
    return result or {"error": "user not found"}


@router.get("/me/stories")
def my_stories(current_user: dict = Depends(require_user)):
    return user_stories(int(current_user["sub"]))


# Saved work
@router.post("/me/saved")
def save(req: SaveWorkRequest, current_user: dict = Depends(require_user)):
    if not req.content.strip():
        raise HTTPException(status_code=400, detail="Content cannot be empty")
    item = save_work(int(current_user["sub"]), req.kind, req.title, req.content)
    return item


@router.get("/me/saved")
def get_saved(kind: str = None, current_user: dict = Depends(require_user)):
    return list_saved_work(int(current_user["sub"]), kind)


@router.delete("/me/saved/{item_id}")
def delete_saved(item_id: int, current_user: dict = Depends(require_user)):
    ok = delete_saved_work(int(current_user["sub"]), item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"deleted": True}


@router.get("/usage")
def usage_info(request: Request, current_user: Optional[dict] = Depends(get_current_user)):
    if not AI_ENABLED:
        return {"ai_enabled": False, "usage": 0, "limit": 0, "remaining": 0}
    if current_user:
        key = f"user:{current_user['sub']}"
        limit = AUTH_DAILY_LIMIT
    else:
        ip = request.client.host if request.client else "unknown"
        key = f"ip:{ip}"
        limit = FREE_DAILY_LIMIT
    used = get_daily_usage(key)
    return {
        "ai_enabled": True,
        "usage": used,
        "limit": limit,
        "remaining": max(0, limit - used),
        "authenticated": current_user is not None,
    }
