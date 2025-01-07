from fastapi import APIRouter

from api.questions.v1.api import router as questions_router
from api.quiz_attempts.v1.api import router as quiz_attempts_router
from api.question_answers.v1.api import router as question_answers_router
from api.auth.v1.api import router as auth_router

api_router_v1 = APIRouter(prefix="/api/v1")
api_router_v1.include_router(questions_router)
api_router_v1.include_router(quiz_attempts_router)
api_router_v1.include_router(question_answers_router)
api_router_v1.include_router(auth_router)