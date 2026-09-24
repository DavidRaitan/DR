from fastapi import APIRouter, Depends
from pydantic import BaseModel
from ..ai import generate_json
from ..prompts import CHARACTER_SYSTEM
from ..samples import character as sample_character
from .rate_limit import ai_rate_limit

router = APIRouter(prefix="/api", tags=["character"])

_CHAR_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"},
        "occupation": {"type": "string"},
        "psychology": {"type": "string"},
        "wound": {"type": "string"},
        "desire": {"type": "string"},
        "contradiction": {"type": "string"},
        "voice": {"type": "string"},
        "physical": {"type": "string"},
        "secret": {"type": "string"},
        "arc": {"type": "string"},
    },
    "required": ["name", "age", "occupation", "psychology", "wound", "desire",
                 "contradiction", "voice", "physical", "secret", "arc"],
}


class CharacterRequest(BaseModel):
    seed: str = ""


@router.post("/character")
def gen_character(req: CharacterRequest, _user=Depends(ai_rate_limit)):
    result = generate_json(CHARACTER_SYSTEM, f"Create a character. Seed: {req.seed or 'anything'}", _CHAR_SCHEMA)
    return result or sample_character(req.seed)
