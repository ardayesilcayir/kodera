"""
Orbital design engine ASGI app (local FastAPI).

Run: ``uvicorn app.main:app --reload`` from the ``optimization_location`` directory.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI

from api.routes_design import router as design_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app = FastAPI(
    title="Orbital Design Engine",
    version="1.0.0",
    description="Regional coverage constellation design API (deterministic optimizer).",
)

app.include_router(design_router)
