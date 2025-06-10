import wfdb
import numpy as np
from scipy.signal import find_peaks
import matplotlib.pyplot as plt



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

def filter_events_by_time(events, start_time, end_time):
    return [
        event for event in events
        if event["end"] >= start_time and event["start"] <= end_time
    ]

def detect_sickness(sampfrom, sampto, tmp_hea_path):

    base_path = tmp_hea_path.with_suffix("")
    record = wfdb.rdrecord(base_path)

    fs = record.fs
    signal = record.p_signal[:, 0]

    r_peaks = detect_r_peaks(signal, fs)
    r_peak_times = r_peaks / fs

    rr_intervals = compute_rr_intervals(r_peaks, fs)
    heart_rates = compute_heart_rate(rr_intervals)

    bradycardia_onsets = detect_bradycardia(r_peak_times[:-1], heart_rates)
    tachycardia_onsets = detect_tachycardia(r_peak_times[:-1], heart_rates)

    #print(f"\nWykryto {len(bradycardia_onsets)} epizodów bradykardii.")
    #for t in bradycardia_onsets:
    #    print(f"Bradykardia wykryta w okolicach {t:.2f} sekundy.")

    #print(f"\nWykryto {len(tachycardia_onsets)} epizodów tachykardii.")
    #for t in tachycardia_onsets:
    #    print(f"Tachykardia wykryta w okolicach {t:.2f} sekundy.")

    all_events = [
        {"start": (t-1.5)*fs, "end": (t+1.5)*fs, "type": "bradycardia"} for t in bradycardia_onsets
    ] + [{"start": (t-1.5)*fs, "end": (t+1.5)*fs, "type": "tachycardia"} for t in tachycardia_onsets]

    start_time = sampfrom / fs
    end_time = sampto / fs

    all_events = filter_events_by_time(all_events, start_time, end_time)

    return all_events
    #print(all_events)



