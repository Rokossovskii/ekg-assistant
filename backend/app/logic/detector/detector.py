import numpy as np
import wfdb
from scipy.signal import find_peaks

def detect_r_peaks(signal, fs):
    distance = int(0.3 * fs)
    threshold = np.percentile(signal, 75)
    peaks, _ = find_peaks(signal, distance=distance, height=threshold)
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

def filter_events_by_time(events, start_time, end_time):
    return [
        event for event in events
        if event["end"] >= start_time and event["start"] <= end_time
    ]

def detect_sickness(sampfrom, sampto, tmp_hea_path):
    base_path = tmp_hea_path.with_suffix("")
    record = wfdb.rdrecord(base_path)

    fs = record.fs
    channel_names = record.sig_name

    if not channel_names:
        raise ValueError("No channels found in the WFDB header.")

    ch_idx = 0  # Using the first available channel
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
    ] + [{"start": s, "end": e, "type": "tachycardia"} for s, e in tachy_events]

    start_time = sampfrom / fs
    end_time = sampto / fs



    all_events.sort(key=lambda ev: ev["start"])
    #all_events=filter_events_by_time(all_events, start_time, end_time)


    return all_events
