from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from config import settings

app = FastAPI(
    title="Theosis API", 
    docs_url="/api/docs", 
    redoc_url="/api/redoc", 
    openapi_url="/api/openapi.json"
)






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