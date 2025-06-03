from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.logic.ekg_endpoints_logic import analyze_image_logic, analyze_signal_logic

ekg_router = APIRouter(prefix="/ekg", tags=["ekg"])

TEMPORAL_FILES_DIR = Path(__file__).parent / "temp"

ALLOWED_IMAGE_TYPES = ["image/png", "image/jpeg", "image/jpg"]
ALLOWED_SIGNAL_EXTENSIONS = [".dat", ".hea"]


@ekg_router.post("/image")
async def analyze_image_endpoint(
    crop_idx: int = 0, image_file: UploadFile = File(...)
) -> JSONResponse:
    if image_file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400, detail="Tylko pliki PNG lub JPG są akceptowane."
        )

    image_bytes = await image_file.read()
    filename = image_file.filename

    processed_data, crop_idx, max_crop_idx, events = analyze_image_logic(
        image_bytes, filename, crop_idx
    )

    return JSONResponse(
        content={
            "channels": processed_data,
            "crop_idx": crop_idx,
            "max_crop_idx": max_crop_idx,
            "events": events,
        }
    )


@ekg_router.post("/signal")
async def analyze_signal_endpoint(
    crop_idx: int = 0,
    hea_file: UploadFile = File(...),
    dat_file: UploadFile = File(...),
    xws_file: UploadFile = File(...),
) -> JSONResponse:
    if not any(hea_file.filename.endswith(ext) for ext in ALLOWED_SIGNAL_EXTENSIONS):
        raise HTTPException(
            status_code=400, detail="Tylko pliki .dat lub .hea są akceptowane."
        )
    if not any(dat_file.filename.endswith(ext) for ext in ALLOWED_SIGNAL_EXTENSIONS):
        raise HTTPException(
            status_code=400, detail="Tylko pliki .dat lub .hea są akceptowane."
        )

    processed_data, crop_idx, max_crop_idx, events = await analyze_signal_logic(
        hea_file, dat_file, xws_file, crop_idx
    )

    return JSONResponse(
        content={
            "channels": processed_data,
            "crop_idx": crop_idx,
            "max_crop_idx": max_crop_idx,
            "events": events,
        }
    )
