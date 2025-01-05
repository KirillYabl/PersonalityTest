from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api.router import api_router_v1
from core.errors_base import ServiceExceptionGroup

def get_application() -> FastAPI:
    application = FastAPI(
        debug=True,
    )
    application.include_router(api_router_v1)

    return application


app = get_application()

@app.exception_handler(ServiceExceptionGroup)
async def service_exception_handler(request: Request, exc_group: ServiceExceptionGroup) -> JSONResponse:
    error_data = exc_group.get_errors_data()
    return JSONResponse(
        status_code=400,
        content={"errors": error_data},
    )