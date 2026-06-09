from fastapi import FastAPI
from src.controllers.haircut_controller import router

app = FastAPI(title="AI Haircut Advisor MVP", version="0.1.0")

app.include_router(router, prefix="/api/v1")
