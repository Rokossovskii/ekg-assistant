import tempfile
from pathlib import Path

from app.logic.detector.detector import detect_sickness

# from app.logic.ecg_digitizer.ecg_digitizer import process_ecg_image
from app.logic.ecg_digitizer.modules.ecg_processor import ECGProcessor
from app.logic.wfdb_converter.wfdb_json_converter import (
    convert_wfdb_to_dict,
    create_window_list,
)


def analyze_image_logic(image_bytes: bytes, filename: str, crop_idx: int) -> list[dict]:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_image_path = Path(tmpdir) / filename

        with open(tmp_image_path, "wb") as f:
            f.write(image_bytes)

        processor = ECGProcessor()
        wfdb_path = processor.process_to_wfdb(tmp_image_path, tmpdir)
        print(f"{wfdb_path}")
        print(list(wfdb_path.parent.iterdir()))
        wfdb_window_list = create_window_list(tmp_hea_path=wfdb_path)
        print(wfdb_window_list)
        crop_idx = min(crop_idx, len(wfdb_window_list) - 1)
        crop_idx = max(crop_idx, -len(wfdb_window_list) + 1)
        processed_data = convert_wfdb_to_dict(
            *wfdb_window_list[crop_idx], tmp_dat_path=wfdb_path
        )
        events = detect_sickness(*wfdb_window_list[crop_idx], tmp_hea_path=wfdb_path)

        return processed_data, crop_idx, len(wfdb_window_list) - 1, events


async def analyze_signal_logic(hea_file, dat_file, xws_file, crop_idx: int = 0) -> dict:
    with tempfile.TemporaryDirectory() as tmpdir:
        hea_filename = hea_file.filename
        dat_filename = dat_file.filename
        xws_filename = xws_file.filename

        tmp_hea_path = Path(tmpdir) / hea_filename
        tmp_dat_path = Path(tmpdir) / dat_filename
        tmp_xws_path = Path(tmpdir) / xws_filename

        with open(tmp_hea_path, "wb") as f:
            f.write(await hea_file.read())

        with open(tmp_dat_path, "wb") as f:
            f.write(await dat_file.read())

        with open(tmp_xws_path, "wb") as f:
            f.write(await xws_file.read())

        wfdb_window_list = create_window_list(
            tmp_hea_path=tmp_hea_path,
            tmp_dat_path=tmp_dat_path,
            tmp_xws_path=tmp_xws_path,
        )
        crop_idx = min(crop_idx, len(wfdb_window_list) - 1)
        crop_idx = max(crop_idx, -len(wfdb_window_list) + 1)
        processed_data = convert_wfdb_to_dict(
            *wfdb_window_list[crop_idx],
            tmp_hea_path=tmp_hea_path,
            tmp_dat_path=tmp_dat_path,
            tmp_xws_path=tmp_xws_path,
        )

  

        events = detect_sickness(*wfdb_window_list[crop_idx], crop_idx, tmp_hea_path=tmp_hea_path)

        return processed_data, crop_idx, len(wfdb_window_list) - 1, events
