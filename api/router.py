from fastapi import APIRouter

from api.questions.v1.api import router as questions_router

api_router_v1 = APIRouter(prefix="/api/v1")
api_router_v1.include_router(questions_router)