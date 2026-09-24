from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

from ..db import (
    list_stories, get_story, create_story, like_story, add_comment,
    GENRES, LENGTHS, STYLES, CRITIQUE_MODES, WORKSHOP_PROMPTS,
)
from ..auth import get_current_user

router = APIRouter(prefix="/api/library", tags=["library"])


class PublishRequest(BaseModel):
    title: str
    body: str
    genre: str = "any"
    length: str = "short"
    style: str = "cinematic"
    critique_mode: str = "open"
    author: str = "Anonymous"


class CommentRequest(BaseModel):
    author: str = "Anonymous"
    body: str
    lens: Optional[str] = None


@router.get("/")
def stories(genre: str = None, length: str = None, style: str = None):
    return {"stories": list_stories(genre, length, style)}


@router.get("/options")
def options():
    return {
        "genres": GENRES,
        "lengths": LENGTHS,
        "styles": STYLES,
        "critique_modes": CRITIQUE_MODES,
        "workshop_prompts": WORKSHOP_PROMPTS,
    }


@router.get("/{story_id}")
def story(story_id: int):
    s = get_story(story_id)
    if not s:
        raise HTTPException(status_code=404, detail="Story not found")
    return s


@router.post("/")
def publish(req: PublishRequest, current_user: Optional[dict] = Depends(get_current_user)):
    uid = int(current_user["sub"]) if current_user else None
    author = current_user.get("username", req.author) if current_user else req.author
    data = {
        "title": req.title,
        "author": author,
        "user_id": uid,
        "body": req.body,
        "genre": req.genre,
        "length": req.length,
        "style": req.style,
        "critique_mode": req.critique_mode,
    }
    return create_story(data)


@router.post("/{story_id}/like")
def like(story_id: int):
    s = get_story(story_id)
    if not s:
        raise HTTPException(status_code=404, detail="Story not found")
    new_likes = like_story(story_id)
    return {"likes": new_likes}


@router.post("/{story_id}/comment")
def comment(story_id: int, req: CommentRequest, current_user: Optional[dict] = Depends(get_current_user)):
    s = get_story(story_id)
    if not s:
        raise HTTPException(status_code=404, detail="Story not found")
    if s["critique_mode"] == "closed":
        raise HTTPException(status_code=403, detail="This story is not accepting comments")
    uid = int(current_user["sub"]) if current_user else None
    author = current_user.get("username", req.author) if current_user else req.author
    return add_comment(story_id, author, req.body, req.lens, uid)
