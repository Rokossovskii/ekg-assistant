from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.logic.ekg_image_logic import process_image
from app.logic.ekg_signal_logic import process_signal

ekg_router = APIRouter(prefix="/ekg", tags=["ekg"])

TEMPORAL_FILES_DIR = Path(__file__).parent / "temp"

ALLOWED_IMAGE_TYPES = ["image/png"]
ALLOWED_SIGNAL_EXTENSIONS = [".dat", ".hea"]


def validate_image(file: UploadFile):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Tylko pliki PNG są akceptowane.")


@ekg_router.post("/image")
async def analyze_image_endpoint(image_file: UploadFile = File(...)) -> JSONResponse:
    validate_image(image_file)
    processed_data = process_image(image_file)
    return JSONResponse(content=processed_data)


def validate_signal(file: UploadFile):
    if not any(file.filename.endswith(ext) for ext in ALLOWED_SIGNAL_EXTENSIONS):
        raise HTTPException(
            status_code=400, detail="Tylko pliki .dat lub .hea są akceptowane."
        )


@ekg_router.post("/signal")
async def analyze_signal_endpoint(signal_file: UploadFile = File(...)) -> JSONResponse:
    validate_signal(signal_file)
    processed_data = process_signal(signal_file)
    return JSONResponse(content=processed_data)
