from typing import Dict, List

from fastapi import UploadFile


def process_signal(signal_file: UploadFile) -> List[Dict[str, object]]:
    leads = [
        {"label": "Lead I", "samples": [0.455, 0.567]},
        {"label": "Lead II", "samples": [0.455, 0.567]},
        {"label": "Lead III", "samples": [0.455, 0.567]},
        {"label": "Lead V1", "samples": [0.455, 0.567]},
    ]
    return leads
