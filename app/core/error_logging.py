import json

from fastapi import Request

from app.db.database import SessionLocal
from app.models.api_error_logs import APIErrorLog


async def log_api_error(
    request: Request,
    response_status: int,
    error_message: str,
    error_code: str | None = None,
    stack_trace: str | None = None,
):
    print(f">>> log_api_error CALLED: {response_status} {error_message}")
    try:
        body_bytes = await request.body()
        try:
            request_body = json.loads(body_bytes) if body_bytes else None
        except Exception:
            request_body = None

        db = SessionLocal()
        try:
            log_entry = APIErrorLog(
                organization_id=getattr(request.state, "organization_id", None),
                user_id=getattr(request.state, "user_id", None),
                endpoint=request.url.path,
                http_method=request.method,
                request_headers=dict(request.headers),
                request_body=request_body,
                response_status=response_status,
                error_code=error_code,
                error_message=error_message,
                stack_trace=stack_trace,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
            )
            db.add(log_entry)
            db.commit()
        finally:
            db.close()

    except Exception as log_exc:
        print(f"[api_error_logs] failed to write log: {log_exc}")