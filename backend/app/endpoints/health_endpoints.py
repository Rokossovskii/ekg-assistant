from fastapi import APIRouter
from fastapi.responses import JSONResponse

health_router = APIRouter(prefix="/health", tags=["health"])


@health_router.get("/live")
async def health_check_ready() -> JSONResponse:
    return JSONResponse(content={"status": True})
