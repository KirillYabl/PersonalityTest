from uuid import UUID
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from api.router import api_router_v1
from core.errors_base import ServiceExceptionGroup
from core.config import settings

def get_application() -> FastAPI:
    application = FastAPI(
        debug=True,
    )
    application.include_router(api_router_v1)

    application.mount("/static", StaticFiles(directory="static"), name="static")

    return application


app = get_application()
templates = Jinja2Templates(directory="templates")

@app.exception_handler(ServiceExceptionGroup)
async def service_exception_handler(request: Request, exc_group: ServiceExceptionGroup) -> JSONResponse:
    error_data = exc_group.get_errors_data()
    return JSONResponse(
        status_code=400,
        content={"errors": error_data},
    )

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request, "quiz_uuid": settings.QUIZ_UUID})

@app.get("/result", response_class=HTMLResponse)
async def read_root(request: Request, quiz_result_uuid: UUID) -> HTMLResponse:
    return templates.TemplateResponse("result.html", {"request": request, "quiz_uuid": settings.QUIZ_UUID, "quiz_result_uuid": quiz_result_uuid})