from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.logic.ekg_image_logic import process_image
from app.logic.ekg_signal_logic import process_signal

from scripts.ecg_digitizer.ecg_digitizer import process_ecg_image

ekg_router = APIRouter(prefix="/ekg", tags=["ekg"])

TEMPORAL_FILES_DIR = Path(__file__).parent / "temp"

ALLOWED_IMAGE_TYPES = ["image/png", "image/jpeg", "image/jpg"]
ALLOWED_SIGNAL_EXTENSIONS = [".dat", ".hea"]


def validate_image(file: UploadFile):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Tylko pliki PNG lub JPG są akceptowane.")


@ekg_router.post("/image")
async def analyze_image_endpoint(image_file: UploadFile = File(...)) -> JSONResponse:
    validate_image(image_file)

    image_bytes = await image_file.read()
    filename = image_file.filename

    processed_data = process_ecg_image(image_bytes, filename)
    return JSONResponse(content=processed_data)


def validate_signal(file: UploadFile):
    if not any(file.filename.endswith(ext) for ext in ALLOWED_SIGNAL_EXTENSIONS):
        raise HTTPException(
            status_code=400, detail="Tylko pliki .dat lub .hea są akceptowane."
        )


@ekg_router.post("/signal")
async def analyze_signal_endpoint(hea_file: UploadFile = File(...), dat_file: UploadFile = File(...)) -> JSONResponse:
    validate_signal(hea_file)
    validate_signal(dat_file)

    processed_data = process_signal(signal_file)
    return JSONResponse(content=processed_data)
