from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy import text

from app.config import settings
from app.db.migrate import run_migrations
from app.db.models import engine
from app.limiter import limiter
from app.ml import symptoms as ml
from app.routers import chat, diseases, prescriptions, profile, symptoms

@asynccontextmanager
async def lifespan(app: FastAPI):
    run_migrations()
    ml.load_artifacts()
    yield


def create_app() -> FastAPI:
    if settings.sentry_dsn:
        sentry_sdk.init(dsn=settings.sentry_dsn, traces_sample_rate=0.1)

    app = FastAPI(title="CureDesk API", version="1.0.0", lifespan=lifespan)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": str(exc.errors()),
                }
            },
        )

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/ready")
    def ready():
        db_ok = False
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            db_ok = True
        except Exception:
            pass
        ml_metrics = ml.get_ml_metrics()
        ml_summary = None
        if ml_metrics:
            ml_summary = {
                "macro_f1": ml_metrics.get("cv_macro_f1"),
                "top3_accuracy": ml_metrics.get("cv_top3_accuracy"),
                "n_classes": ml_metrics.get("n_classes"),
            }
        return {
            "status": "ready" if db_ok and ml.is_ready() else "degraded",
            "db": db_ok,
            "ml": ml.is_ready(),
            "ml_metrics": ml_summary,
        }

    app.include_router(symptoms.router)
    app.include_router(diseases.router)
    app.include_router(chat.router)
    app.include_router(prescriptions.router)
    app.include_router(profile.router)

    return app


app = create_app()
