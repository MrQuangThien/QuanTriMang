from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from api.routers import backup, devices, diff, gns3, metrics, restore
from config.settings import APP_HOST, APP_NAME, APP_PORT
from core.connector import load_devices
from storage.db import init_db, list_backups

app = FastAPI(
    title=APP_NAME,
    version="1.0.0",
)

app.mount(
    "/static",
    StaticFiles(directory="web/static"),
    name="static",
)

templates = Jinja2Templates(
    directory="web/templates"
)

app.include_router(devices.router)
app.include_router(backup.router)
app.include_router(diff.router)
app.include_router(metrics.router)
app.include_router(restore.router)
app.include_router(gns3.router)


@app.on_event("startup")
def startup():
    print("[APP] Network AutoManager starting...")
    init_db()
    print("[APP] Database initialized")


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "devices": load_devices(),
            "title": APP_NAME,
        },
    )



@app.get("/devices", response_class=HTMLResponse)
def devices_page(request: Request):
    return templates.TemplateResponse(request=request, name="devices.html", context={"request": request, "title": APP_NAME})

@app.get("/backups", response_class=HTMLResponse)
def backups_page(request: Request):
    return templates.TemplateResponse(request=request, name="backups.html", context={"request": request, "title": APP_NAME})

@app.get("/diff", response_class=HTMLResponse)
def diff_page(request: Request):
    return templates.TemplateResponse(request=request, name="diff.html", context={"request": request, "title": APP_NAME})

@app.get("/restore", response_class=HTMLResponse)
def restore_page(request: Request):
    return templates.TemplateResponse(request=request, name="restore.html", context={"request": request, "title": APP_NAME})

@app.get("/monitoring", response_class=HTMLResponse)
def monitoring_page(request: Request):
    return templates.TemplateResponse(request=request, name="monitoring.html", context={"request": request, "title": APP_NAME})

@app.get("/gns3", response_class=HTMLResponse)
def gns3_page(request: Request):
    return templates.TemplateResponse(request=request, name="gns3.html", context={"request": request, "title": APP_NAME})

@app.get("/activity", response_class=HTMLResponse)
def activity_page(request: Request):
    return templates.TemplateResponse(request=request, name="activity.html", context={"request": request, "title": APP_NAME})

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": APP_NAME,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host=APP_HOST,
        port=APP_PORT,
        reload=True,
    )
