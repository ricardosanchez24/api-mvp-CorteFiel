from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mi_app_de_cortes.src.controllers import haircut_controller

load_dotenv()

app = FastAPI(
    title="AI Haircut Advisor MVP",
    description="API para recomendación de cortes de cabello con IA",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(haircut_controller.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "AI Haircut Advisor API running"}


@app.get("/health")
def health():
    return {"status": "ok"}
