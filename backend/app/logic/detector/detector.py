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

def detect_bradycardia(times, hr, window_duration=3.0, threshold=60):
    bradycardia_times = []
    for i in range(len(hr)):
        window_start = times[i]
        window_end = window_start + window_duration
        in_window = (times >= window_start) & (times <= window_end)
        if np.sum(in_window) > 0:
            avg_hr = np.mean(hr[in_window])
            if avg_hr < threshold:
                bradycardia_times.append(window_start)
    return bradycardia_times

def detect_tachycardia(times, hr, window_duration=3.0, threshold=100):
    tachycardia_times = []
    for i in range(len(hr)):
        window_start = times[i]
        window_end = window_start + window_duration
        in_window = (times >= window_start) & (times <= window_end)
        if np.sum(in_window) > 0:
            avg_hr = np.mean(hr[in_window])
            if avg_hr > threshold:
                tachycardia_times.append(window_start)
    return tachycardia_times

def group_events(event_times, duration=3.0):
    if not event_times:
        return []
    
    grouped = []
    start = event_times[0]
    end = start + duration
    
    for t in event_times[1:]:
        if t <= end:
            end = t + duration
        else:
            grouped.append((start, end))
            start = t
            end = t + duration
    grouped.append((start, end))
    return grouped

def detect_sickness(tmp_hea_path):
    base_path = tmp_hea_path.with_suffix("")
    record = wfdb.rdrecord(base_path)

    fs = record.fs
    channel_names = record.sig_name

    if not channel_names:
        raise ValueError("No channels found in the WFDB header.")
    
    ch_idx = 0
    signal = record.p_signal[:, ch_idx]

    r_peaks = detect_r_peaks(signal, fs)
    r_peak_times = r_peaks / fs

    rr_intervals = compute_rr_intervals(r_peaks, fs)
    heart_rates = compute_heart_rate(rr_intervals)

    brady_times = detect_bradycardia(r_peak_times[:-1], heart_rates)
    tachy_times = detect_tachycardia(r_peak_times[:-1], heart_rates)

    brady_events = group_events(brady_times)
    tachy_events = group_events(tachy_times)

    all_events = [
        {"start": s, "end": e, "type": "bradycardia"} for s, e in brady_events
    ] + [
        {"start": s, "end": e, "type": "tachycardia"} for s, e in tachy_events
    ]

    all_events.sort(key=lambda ev: ev["start"])

    return all_events
