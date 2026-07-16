from fastapi import FastAPI
from sqlalchemy import text

from app.db.database import engine


from app.api.organizations import router as organizations_router
from app.api.api_error_logs import router as api_error_logs_router

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
    api_error_logs_router,
    prefix="/api/v1",
)