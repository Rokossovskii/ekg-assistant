from fastapi import FastAPI

from app.endpoints.ekg_endpoints import ekg_router
from app.endpoints.health_endpoints import health_router

app = FastAPI()

app.include_router(ekg_router)
app.include_router(health_router)
