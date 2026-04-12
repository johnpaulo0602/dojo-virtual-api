import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.academic.routers import router as academic_router
from src.classes.routers import router as classes_router
from src.financial.routers import router as financial_router
from src.identity.routers import router as auth_router, users_router
from src.dashboard.routers import router as dashboard_router
from src.config.routers import router as config_router
from src.core.setup import create_initial_admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    await create_initial_admin()
    yield
    # Shutdown actions

app = FastAPI(title="Jiu-Jitsu Management API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(academic_router)
app.include_router(classes_router)
app.include_router(financial_router)
app.include_router(dashboard_router)
app.include_router(config_router)

@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}

# Static files must be mounted AFTER all routers
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
