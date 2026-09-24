from fastapi import APIRouter, Depends
from pydantic import BaseModel
from ..ai import generate_json
from ..prompts import WORLD_SYSTEM, MAGIC_SYSTEM
from ..samples import world_setting, world_species, magic_hard, magic_soft
from .rate_limit import ai_rate_limit

router = APIRouter(prefix="/api/world", tags=["world"])

_SETTING_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "geography": {"type": "string"},
        "climate": {"type": "string"},
        "culture": {"type": "string"},
        "conflict": {"type": "string"},
    },
    "required": ["name", "geography", "climate", "culture", "conflict"],
}

_SPECIES_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "origin": {"type": "string"},
        "biology": {"type": "string"},
        "culture": {"type": "string"},
        "tension": {"type": "string"},
    },
    "required": ["name", "origin", "biology", "culture", "tension"],
}

_MAGIC_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "source": {"type": "string"},
        "mechanics": {"type": "string"},
        "cost": {"type": "string"},
        "limits": {"type": "string"},
        "thematic_resonance": {"type": "string"},
    },
    "required": ["name", "source", "mechanics", "cost", "limits", "thematic_resonance"],
}

_SOFT_MAGIC_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "nature": {"type": "string"},
        "expression": {"type": "string"},
        "cultural_status": {"type": "string"},
        "mystery": {"type": "string"},
    },
    "required": ["name", "nature", "expression", "cultural_status", "mystery"],
}


class SeedRequest(BaseModel):
    seed: str = ""


@router.post("/setting")
def gen_setting(req: SeedRequest, _user=Depends(ai_rate_limit)):
    result = generate_json(WORLD_SYSTEM, f"Seed: {req.seed or 'anything'}", _SETTING_SCHEMA)
    return result or world_setting(req.seed)


@router.post("/species")
def gen_species(req: SeedRequest, _user=Depends(ai_rate_limit)):
    result = generate_json(WORLD_SYSTEM, f"Create a species/people. Seed: {req.seed or 'anything'}", _SPECIES_SCHEMA)
    return result or world_species(req.seed)


@router.post("/magic")
def gen_magic(req: SeedRequest, _user=Depends(ai_rate_limit)):
    kind = req.seed.lower()
    if "soft" in kind:
        result = generate_json(MAGIC_SYSTEM, f"Create a SOFT magic system. Seed: {req.seed}", _SOFT_MAGIC_SCHEMA)
        return result or magic_soft(req.seed)
    result = generate_json(MAGIC_SYSTEM, f"Create a HARD magic system with strict rules. Seed: {req.seed or 'anything'}", _MAGIC_SCHEMA)
    return result or magic_hard(req.seed)
