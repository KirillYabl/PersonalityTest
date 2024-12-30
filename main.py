from fastapi import FastAPI

def get_application() -> FastAPI:
    application = FastAPI(
        debug=True,
    )

    return application


app = get_application()

@app.get(path="/")
async def get_root() -> str:
    return "Hello world"