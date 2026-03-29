"""
ORBITA-R — Regional Constellation Optimization System
FastAPI application entrypoint
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import design, scenario, coverage, risk, optimizer, auth, maneuver

# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title="ORBITA-R API",
    description=(
        "**ORBITA-R** — Regional Constellation Optimization System\n\n"
        "Bu API, kullanıcı tarafından seçilen coğrafi bölge ve görev amacına göre "
        "7/24 kesintisiz kapsama sağlayacak optimum uydu takım mimarisini tasarlar.\n\n"
        "## Modlar\n"
        "- **Mission-Based Design** — Sıfırdan constellation tasarımı\n"
        "- **Real-World Scenario** — Mevcut uydu seti üzerinden optimizasyon\n\n"
        "## Temel Özellikler\n"
        "- Coverage analizi (ratio, continuity, revisit, gap)\n"
        "- Failure simulation & risk analizi\n"
        "- Minimum uydu sayısı optimizasyonu\n"
        "- Trade-off önerileri (Cost / Balanced / Resilient)\n"
        "- Explainable sonuçlar\n"
    ),
    version="0.1.0",
    contact={
        "name": "ORBITA-R Team",
    },
    license_info={
        "name": "MIT",
    },
    openapi_tags=[
        {
            "name": "design",
            "description": "Mission-Based Design akışı — sıfırdan constellation tasarımı.",
        },
        {
            "name": "scenario",
            "description": "Real-World Scenario akışı — mevcut uydu seti üzerinden optimizasyon.",
        },
        {
            "name": "coverage",
            "description": "Bölge bazlı kapsama analizi.",
        },
        {
            "name": "risk",
            "description": "Failure simulation ve risk değerlendirmesi.",
        },
        {
            "name": "optimizer",
            "description": "Minimum uydu sayısı ve optimizasyon yardımcıları.",
        },
        {
            "name": "auth",
            "description": "Supabase JWT Kimlik doğrulama işlemleri.",
        },
    ],
)

# ---------------------------------------------------------------------------
# CORS Middleware
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Geliştirme aşamasında tüm originlere açık
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

API_V1_PREFIX = "/api/v1"

app.include_router(design.router,    prefix=API_V1_PREFIX + "/design", tags=["design"])
app.include_router(maneuver.router,  prefix=API_V1_PREFIX + "/maneuver", tags=["maneuver"])
# app.include_router(scenario.router,  prefix=API_V1_PREFIX + "/scenario", tags=["scenario"])
# app.include_router(coverage.router,  prefix=API_V1_PREFIX + "/coverage", tags=["coverage"])
# app.include_router(risk.router,      prefix=API_V1_PREFIX + "/risk", tags=["risk"])
# app.include_router(optimizer.router, prefix=API_V1_PREFIX + "/optimizer", tags=["optimizer"])
app.include_router(auth.router,      prefix=API_V1_PREFIX + "/auth", tags=["auth"])


# ---------------------------------------------------------------------------
# Root health-check
# ---------------------------------------------------------------------------

@app.get("/", include_in_schema=False)
async def root() -> dict:
    return {
        "service": "ORBITA-R API",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["health"])
async def health() -> dict:
    """Servis sağlık kontrolü."""
    return {"status": "ok"}
