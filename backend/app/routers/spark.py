from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional

from ..ai import generate_text
from ..prompts import SPARK_SYSTEM, spark_user, CONTINUE_SYSTEM
from ..samples import spark as sample_spark, continuation as sample_continuation
from ..db import GENRES
from .rate_limit import ai_rate_limit

router = APIRouter(prefix="/api", tags=["spark"])


class SparkRequest(BaseModel):
    genre: str = "any"
    focus: str = ""


class ContinueRequest(BaseModel):
    story: str
    max_tokens: Optional[int] = 300


@router.post("/spark")
def get_spark(req: SparkRequest, _user=Depends(ai_rate_limit)):
    text = generate_text(SPARK_SYSTEM, spark_user(req.genre, req.focus), max_tokens=300)
    return {"spark": text or sample_spark(req.genre, req.focus), "ai": text is not None}


@router.post("/continue")
def continue_story(req: ContinueRequest, _user=Depends(ai_rate_limit)):
    text = generate_text(CONTINUE_SYSTEM, req.story, max_tokens=req.max_tokens)
    return {"continuation": text or sample_continuation(req.story), "ai": text is not None}


@router.get("/spark/options")
def spark_options():
    return {"genres": GENRES}
