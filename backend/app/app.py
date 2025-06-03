from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.endpoints.ekg_endpoints import ekg_router
from app.endpoints.health_endpoints import health_router

app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://igorstalmach.github.io",
    "https://igorstalmach.github.io/ecg-visualizer/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(ekg_router)
app.include_router(health_router)
