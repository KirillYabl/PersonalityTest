from fastapi import FastAPI

from api.router import api_router_v1

def get_application() -> FastAPI:
    application = FastAPI(
        debug=True,
    )

    return application


app = get_application()
app.include_router(api_router_v1)