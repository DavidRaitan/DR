from fastapi import APIRouter, Depends
from pydantic import BaseModel
from ..ai import generate_json
from ..prompts import SCENE_SYSTEM
from ..samples import scene_analysis as sample_scene
from .rate_limit import ai_rate_limit

router = APIRouter(prefix="/api/structure", tags=["structure"])

_SCENE_SCHEMA = {
    "type": "object",
    "properties": {
        "act": {"type": "string"},
        "function": {"type": "string"},
        "analysis": {"type": "string"},
        "what_works": {"type": "string"},
        "suggestion": {"type": "string"},
    },
    "required": ["act", "function", "analysis", "what_works", "suggestion"],
}

THREE_ACT = {
    "title": "The Three-Act Structure",
    "overview": "A dramatic framework that organizes narrative into three distinct phases of tension and release.",
    "acts": [
        {
            "name": "Act I — Setup",
            "purpose": "Establish the world, the protagonist, and the central conflict. End with an inciting incident that shatters the status quo.",
            "key_beats": ["Opening image", "Status quo / ordinary world", "Inciting incident", "Threshold crossing / lock-in"],
            "length": "Roughly 25% of the story",
        },
        {
            "name": "Act II — Confrontation",
            "purpose": "Escalate the conflict through a series of complications, reversals, and rising stakes. The protagonist must change or fail.",
            "key_beats": ["First complication", "Midpoint reversal or revelation", "All-is-lost moment", "Dark night of the soul"],
            "length": "Roughly 50% of the story",
        },
        {
            "name": "Act III — Resolution",
            "purpose": "Bring the conflict to its climax and resolve the central question. Show how the protagonist has transformed.",
            "key_beats": ["Climax / decisive action", "Resolution of all subplots", "Closing image (mirrors or contrasts opening)"],
            "length": "Roughly 25% of the story",
        },
    ],
    "tips": [
        "Every scene should move the protagonist closer to or further from their goal.",
        "The midpoint must change the story's direction — not just complicate it.",
        "The all-is-lost moment should feel genuinely hopeless. If there's an obvious solution, you haven't gone far enough.",
        "The closing image should rhyme with the opening — same location, same action, but charged with new meaning.",
    ],
}


class SceneRequest(BaseModel):
    scene: str


@router.get("/three-act")
def three_act():
    return THREE_ACT


@router.post("/classify-scene")
def classify_scene(req: SceneRequest, _user=Depends(ai_rate_limit)):
    result = generate_json(SCENE_SYSTEM, req.scene, _SCENE_SCHEMA)
    return result or sample_scene(req.scene)
