from fastapi import FastAPI

from app.endpoints.ekg_endpoints import ekg_router

app = FastAPI()

app.include_router(ekg_router)
