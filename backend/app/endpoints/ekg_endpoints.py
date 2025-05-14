import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from ..logic.ecg_digitizer.ecg_digitizer import process_ecg_image
from ..logic.wfdb_converter.wfdb_json_converter import convert_wfdb_to_dict

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

    return JSONResponse(content={
        "start_time": '',
        "end_time": '',
        "channels": processed_data
    })


def validate_signal(file: UploadFile):
    if not any(file.filename.endswith(ext) for ext in ALLOWED_SIGNAL_EXTENSIONS):
        raise HTTPException(
            status_code=400, detail="Tylko pliki .dat lub .hea są akceptowane."
        )


@ekg_router.post("/signal")
async def analyze_signal_endpoint(
        hea_file: UploadFile = File(...),
        dat_file: UploadFile = File(...),
        xws_file: UploadFile = File(...)) -> JSONResponse:

    validate_signal(hea_file)
    validate_signal(dat_file)

    with tempfile.TemporaryDirectory() as tmpdir:
        hea_filename = hea_file.filename
        dat_filename = dat_file.filename

        tmp_hea_path = Path(tmpdir) / hea_filename
        tmp_dat_path = Path(tmpdir) / dat_filename

        with open(tmp_hea_path, "wb") as f:
            f.write(await hea_file.read())

        with open(tmp_dat_path, "wb") as f:
            f.write(await dat_file.read())

        processed_data = convert_wfdb_to_dict(tmpdir + "/" + hea_filename.split(".")[0])

    return JSONResponse(content={
        "start_time": '',
        "end_time": '',
        "channels": processed_data
    })
