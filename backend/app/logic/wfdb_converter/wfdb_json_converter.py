from pathlib import Path

import wfdb

WDFDB_SAMPLES_PER_WINDOW = 1000


# def convert_wfdb_to_dict(record_path):
#     """
#     Loads a WFDB record and converts it into a list of dictionaries
#     with labels and samples for each signal channel.

#     Parameters:
#         record_path (str): Full or relative path to the WFDB record (without extension)

#     Returns:
#         list[dict]: A list of dicts with 'label' and 'samples' keys.
#     """

#     # Strip known WFDB file extensions if provided
#     known_extensions = [".hea", ".dat", ".atr", ".ann"]
#     base, ext = os.path.splitext(record_path)
#     if ext.lower() in known_extensions:
#         record_path = base

#     # Get absolute path (no splitting!)
#     full_path = os.path.abspath(record_path)

#     # Check that required files exist
#     hea_file = full_path + ".hea"
#     dat_file = full_path + ".dat"
#     if not (os.path.isfile(hea_file) and os.path.isfile(dat_file)):
#         raise FileNotFoundError(
#             f"Expected WFDB files not found:\n - {hea_file}\n - {dat_file}"
#         )

#     try:
#         record_info = wfdb.rdheader(full_path)
#         total_samples = record_info.sig_len

#         max_samples = 2000
#         end_sample = min(max_samples, total_samples)

#         record = wfdb.rdrecord(full_path, sampto=end_sample)
#     except Exception as e:
#         raise RuntimeError(f"Could not read WFDB record at '{full_path}': {e}")

#     if record.p_signal is None:
#         raise ValueError("No signal data found in the record.")

#     signal_data = record.p_signal
#     channel_names = record.sig_name

#     result = []
#     for idx, label in enumerate(channel_names):
#         samples = signal_data[:, idx].tolist()
#         result.append({"label": label, "samples": samples})

#     print(json.dumps(result, indent=2))
#     return result


def create_window_list(**kwargs):
    tmp_hea_path: Path = kwargs.pop("tmp_hea_path", None)
    base_path = tmp_hea_path.with_suffix("")
    try:
        total_samples = wfdb.rdheader(base_path)
    except Exception as e:
        raise RuntimeError(f"Could not read WFDB record at '{tmp_hea_path}': {e}")
    return [
        (x - WDFDB_SAMPLES_PER_WINDOW, x)
        for x in range(
            WDFDB_SAMPLES_PER_WINDOW,
            total_samples.sig_len - 1,
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
