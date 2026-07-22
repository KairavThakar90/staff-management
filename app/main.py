from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy import text
import traceback

from app.db.database import engine
from app.core.error_logging import log_api_error

from app.api.organizations import router as organizations_router
from app.api.api_error_logs import router as api_error_logs_router
from app.api.projects import router as projects_router
from app.api.tasks import router as tasks_router
from app.api.time_entry_activity import router as time_entry_activity_router
from app.api.time_entry_app_usage import router as time_entry_app_usage_router
from app.api.time_entries import router as time_entries_router

app = FastAPI(
    title="SMS Backend API",
    description="Employee Tracking & Productivity Management System Backend",
    version="1.0.0",
)


# --- Catches HTTPException (404, 409, 400, etc. raised deliberately) ---
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    await log_api_error(
        request=request,
        response_status=exc.status_code,
        error_message=str(exc.detail),
        error_code=f"HTTP_{exc.status_code}",
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )



# --- Catches unhandled exceptions (AttributeError, TypeError, etc. -> 500) ---
# @app.exception_handler(Exception)
# async def unhandled_exception_handler(request: Request, exc: Exception):
#     tb = traceback.format_exc()
#     await log_api_error(
#         request=request,
#         response_status=500,
#         error_message=str(exc),
#         error_code="INTERNAL_SERVER_ERROR",
#         stack_trace=tb,
#     )
#     return JSONResponse(
#         status_code=500,
#         content={"detail": "Internal server error"},
#     )


@app.get("/")
def root():
    return {"message": "Welcome to SMS Backend!"}


@app.get("/health/database")
def database_health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "success", "database": "Connected to Neon PostgreSQL"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}


app.include_router(
    organizations_router, 
    prefix="/api/v1"
)
app.include_router(
    projects_router,
    prefix="/api/v1"
)
app.include_router(
    tasks_router,
    prefix="/api/v1"
)
app.include_router(
    time_entries_router,
    prefix="/api/v1"
)
app.include_router(
    time_entry_activity_router,
    prefix="/api/v1"
)
app.include_router(
    time_entry_app_usage_router,
    prefix="/api/v1"
)
app.include_router(
    api_error_logs_router, 
    prefix="/api/v1"
    )