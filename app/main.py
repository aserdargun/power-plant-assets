from __future__ import annotations

from fastapi import FastAPI

from . import models
from .database import engine
from .routers import assets, workorders


def create_app() -> FastAPI:
    app = FastAPI(
        title="Power Plant Assets API",
        description="Track generation assets and maintenance work orders.",
        version="0.1.0",
    )

    # Ensure tables exist when the service starts. In production use migrations.
    models.Base.metadata.create_all(bind=engine)

    app.include_router(assets.router)
    app.include_router(workorders.router)
    return app


app = create_app()
