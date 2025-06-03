import wfdb
import numpy as np
from scipy.signal import find_peaks

def detect_r_peaks(signal, fs):
    distance = int(0.6 * fs)
    peaks, _ = find_peaks(signal, distance=distance, height=np.mean(signal))
    return peaks

def compute_rr_intervals(r_peaks, fs):
    return np.diff(r_peaks) / fs

def compute_heart_rate(rr_intervals):
    return 60 / rr_intervals

def detect_events(times, hr, threshold, comparison, label):
    result = []
    window_duration = 3.0
    for i in range(len(hr)):
        window_start = times[i]
        window_end = window_start + window_duration
        in_window = (times >= window_start) & (times <= window_end)
        if np.sum(in_window) > 0:
            avg_hr = np.mean(hr[in_window])
            if comparison(avg_hr, threshold):
                result.append({
                    "start_time": round(window_start, 2),
                    "end_time": round(window_end, 2),
                    "type": label
                })
    return result

def detect_brady_tachy_events(sampfrom, sampto, **kwargs):
    tmp_dat_path = kwargs.pop("tmp_dat_path", None)
    base_path = tmp_dat_path.with_suffix("")
    try:
        record = wfdb.rdrecord(base_path, sampfrom=sampfrom, sampto=sampto)
    except Exception as e:
        raise RuntimeError(f"Could not read WFDB record at '{tmp_dat_path}': {e}")

    if record.p_signal is None:
        raise ValueError("No signal data found in the record.")

    signal = record.p_signal[:, 0]
    fs = record.fs

    r_peaks = detect_r_peaks(signal, fs)
    r_peak_times = r_peaks / fs
    rr_intervals = compute_rr_intervals(r_peaks, fs)
    heart_rates = compute_heart_rate(rr_intervals)

    brady_events = detect_events(
        r_peak_times[:-1], heart_rates, 60, lambda x, t: x < t, "bradycardia"
    )
    tachy_events = detect_events(
        r_peak_times[:-1], heart_rates, 100, lambda x, t: x > t, "tachycardia"
    )

    return brady_events + tachy_events
