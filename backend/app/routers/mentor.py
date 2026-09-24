from fastapi import APIRouter, Depends
from pydantic import BaseModel
from ..ai import generate_text
from ..prompts import MENTORS
from .rate_limit import ai_rate_limit

router = APIRouter(prefix="/api/mentor", tags=["mentor"])


class AskRequest(BaseModel):
    mentor: str
    question: str


@router.get("/")
def list_mentors():
    return [
        {"id": k, "name": v["name"], "focus": v["focus"]}
        for k, v in MENTORS.items()
    ]


@router.post("/ask")
def ask_mentor(req: AskRequest, _user=Depends(ai_rate_limit)):
    mentor = MENTORS.get(req.mentor)
    if not mentor:
        return {"reply": "Unknown mentor. Choose from: architect, philosopher, historian, editor, critic.", "ai": False}
    reply = generate_text(mentor["system"], req.question, max_tokens=600)
    if not reply:
        reply = (
            f"I'm {mentor['name']}, focused on {mentor['focus']}. "
            "I can't connect to my thoughts right now — but I'm here. "
            "Ask me anything about your work, and when the connection returns, I'll give you my full attention."
        )
    return {"reply": reply, "mentor": {"id": req.mentor, "name": mentor["name"]}, "ai": reply is not None}
