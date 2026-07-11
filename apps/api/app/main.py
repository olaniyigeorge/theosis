from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import sqlalchemy
import uvicorn

from config import settings
from .utils.logger import logger
from .db.index import db_manager
from .infra.redis import redis_manager
from .routers.index import router_list


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup...")
    app.state.redis = None

    try:
        engine_kwargs = {}
        if "sqlite" in settings.DATABASE_URL:
            engine_kwargs.update({
                "connect_args": {"check_same_thread": False},
                "poolclass": sqlalchemy.StaticPool,
            })

        db_manager.initialize(settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1), **engine_kwargs)
        await db_manager.create_tables()

        app.state.redis = await redis_manager.initialize(
            url=settings.REDIS_URL,
            decode_responses=True,
        )

        logger.info("Application startup complete")
        yield

    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

    finally:
        await redis_manager.close()
        await db_manager.close()
        logger.info("Application shutdown complete")


app = FastAPI(
    title="Theosis API", 
    docs_url="/api/docs", 
    redoc_url="/api/redoc", 
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)


# --- Routers ---
for router in router_list:
    app.include_router(router)


# --- Static & Templates ---
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# --- Routes ---
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    docs_href = f"{settings.DOMAIN}/api/docs"
    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "name": "Theosis Backend",
            "details": "Theosis API Backend",
            "docs_href": docs_href,
        },
    )





@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True)