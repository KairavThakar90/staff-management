from fastapi import FastAPI
from sqlalchemy import text

from app.db.database import engine
import app.models

from app.api.organizations import router as organizations_router
from app.api.users import router as users_router
from app.api.roles import router as roles_router
from app.api.permissions import router as permissions_router
from app.api.projects import router as projects_router
from app.api.tasks import router as tasks_router
from app.api.time_sessions import router as time_sessions_router

app = FastAPI(
    title="SMS Backend API",
    description="Employee Tracking & Productivity Management System Backend",
    version="1.0.0",
)


@app.get("/")
def root():
    return {"message": "Welcome to SMS Backend!"}


@app.get("/health/database")
def database_health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "success",
            "database": "Connected to Neon PostgreSQL",
        }

    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
        }
    

app.include_router(
    organizations_router,
    prefix="/api/v1",
    
)

app.include_router(
    users_router,
    prefix="/api/v1",
   
)

app.include_router(
    roles_router,
    prefix="/api/v1",
    
)

app.include_router(
    permissions_router,
    prefix="/api/v1",
)

app.include_router(
    projects_router,
    prefix="/api/v1",
)

app.include_router(
    tasks_router,
    prefix="/api/v1",
)

app.include_router(
    time_sessions_router,
    prefix="/api/v1",
)
#this is comment