from pathlib import Path

import wfdb

WDFDB_SAMPLES_PER_WINDOW = 4000


def create_window_list(**kwargs):
    tmp_hea_path: Path = kwargs.pop("tmp_hea_path", None)
    base_path = tmp_hea_path.with_suffix("")
    try:
        total_samples = wfdb.rdheader(base_path)
        print(f"Total samples in record: {total_samples.sig_len}")
    except Exception as e:
        raise RuntimeError(f"Could not read WFDB record at '{tmp_hea_path}': {e}")
    return [
        (x - WDFDB_SAMPLES_PER_WINDOW, min(x, total_samples.sig_len - 1))
        for x in range(
            WDFDB_SAMPLES_PER_WINDOW,
            total_samples.sig_len - 1 + WDFDB_SAMPLES_PER_WINDOW,
            WDFDB_SAMPLES_PER_WINDOW,
        )
    ]


def convert_wfdb_to_dict(sampfrom, sampto, **kwargs):
    tmp_dat_path = kwargs.pop("tmp_dat_path", None)
    base_path = tmp_dat_path.with_suffix("")
    try:
        record = wfdb.rdrecord(base_path, sampfrom=sampfrom, sampto=sampto)
    except Exception as e:
        raise RuntimeError(f"Could not read WFDB record at '{tmp_dat_path}': {e}")

    if record.p_signal is None:
        raise ValueError("No signal data found in the record.")

    signal_data = record.p_signal
    channel_names = record.sig_name

    result = []
    for idx, label in enumerate(channel_names):
        samples = signal_data[:, idx].tolist()
        result.append({"label": label, "samples": samples})

    return result
