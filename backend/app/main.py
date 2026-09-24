from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from .config import FRONTEND_DIR, AI_ENABLED, ACTIVE_PROVIDER
from .db import init_db
from .ai import provider_info
from .routers import spark, worldbuilder, character, structure, library, mentor, auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="Just Wright", lifespan=lifespan)

app.include_router(spark.router)
app.include_router(worldbuilder.router)
app.include_router(character.router)
app.include_router(structure.router)
app.include_router(library.router)
app.include_router(mentor.router)
app.include_router(auth_router.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "app": "Just Wright", **provider_info()}


if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/{full_path:path}")
    def spa(full_path: str):
        index = FRONTEND_DIR / "index.html"
        return FileResponse(str(index))
