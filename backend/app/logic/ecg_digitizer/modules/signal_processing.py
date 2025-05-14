import numpy as np
import matplotlib.pyplot as plt
from scipy import signal, interpolate
import cv2


def extract_signal(binary_image, debug_dir=None):
    height, width = binary_image.shape
    x_values = []
    y_values = []

    baseline_y = height // 2

    for x in range(width):
        white_pixels = np.where(binary_image[:, x] > 0)[0]

        if len(white_pixels) > 0:
            avg_y = np.mean(white_pixels)
            is_upward = avg_y < baseline_y

            if is_upward:
                y = np.min(white_pixels)
            else:
                y = np.max(white_pixels)

            x_values.append(x)
            y_values.append(baseline_y - y)

    if debug_dir is not None:
        _visualize_extracted_signal(x_values, y_values, binary_image, debug_dir)

    return x_values, y_values


def _visualize_extracted_signal(x_values, y_values, binary_image, debug_dir):
    plt.figure(figsize=(12, 6))

    plt.subplot(211)
    plt.imshow(binary_image, cmap='gray')
    plt.title('Binary ECG Image')

    height = binary_image.shape[0]
    baseline_y = height // 2
    for x, y in zip(x_values, y_values):
        image_y = baseline_y - y
        plt.plot(x, image_y, 'r.', markersize=2)

    plt.subplot(212)
    plt.plot(x_values, y_values, 'b-', linewidth=1)
    plt.title('Extracted ECG Signal')
    plt.grid(True, alpha=0.3)
    plt.axhline(y=0, color='r', linestyle='-', alpha=0.3)

    plt.tight_layout()
    plt.savefig(f"{debug_dir}/extracted_signal.png")
    plt.close()


def detect_grid_size(image, debug_dir=None):
    height, width = image.shape

    margin_height = max(int(height * 0.15), 20)
    top_margin = image[:margin_height, :]
    bottom_margin = image[height - margin_height:, :]
    combined_margins = np.vstack((top_margin, bottom_margin))

    enhanced_margins = cv2.adaptiveThreshold(
        combined_margins, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 15, 2
    )

    h_projection = np.sum(enhanced_margins, axis=0)
    v_projection = np.sum(enhanced_margins, axis=1)

    small_grid_x = _detect_grid_spacing_fft(h_projection)
    small_grid_y = _detect_grid_spacing_fft(v_projection)

    if small_grid_x <= 0 or small_grid_x > width / 10:
        small_grid_x = _detect_grid_spacing_peaks(h_projection)

    if small_grid_y <= 0 or small_grid_y > height / 10:
        small_grid_y = _detect_grid_spacing_peaks(v_projection)

    if small_grid_x <= 0 or small_grid_x > width / 10:
        small_grid_x = width / 50

    if small_grid_y <= 0 or small_grid_y > height / 10:
        small_grid_y = height / 50

    if abs(small_grid_x - small_grid_y) < max(small_grid_x, small_grid_y) * 0.3:
        small_grid_size = (small_grid_x + small_grid_y) / 2
    else:
        small_grid_size = small_grid_x

    large_grid_size = small_grid_size * 5

    if debug_dir is not None:
        _visualize_grid_detection(
            image, small_grid_size, large_grid_size, debug_dir
        )

    return small_grid_size, large_grid_size


def _detect_grid_spacing_fft(projection):
    if np.std(projection) < 1e-6:
        return -1

    normalized = projection - np.mean(projection)

    fft_result = np.abs(np.fft.fft(normalized))
    freqs = np.fft.fftfreq(len(normalized))

    pos_mask = (freqs > 0) & (freqs < 0.5)
    freqs_pos = freqs[pos_mask]
    fft_pos = fft_result[pos_mask]

    peaks, _ = signal.find_peaks(fft_pos, height=0.1 * np.max(fft_pos), distance=5)

    if len(peaks) == 0:
        return -1

    dominant_peak = peaks[np.argmax(fft_pos[peaks])]
    dominant_freq = freqs_pos[dominant_peak]

    return 1.0 / dominant_freq


def _detect_grid_spacing_peaks(projection):
    try:
        normalized = projection / np.max(projection)

        smoothed = signal.savgol_filter(normalized, 11, 3)

        peaks, _ = signal.find_peaks(
            smoothed, height=0.2, distance=5, prominence=0.05
        )

        if len(peaks) < 3:
            return -1

        distances = np.diff(peaks)

        if len(distances) > 3:
            q1 = np.percentile(distances, 25)
            q3 = np.percentile(distances, 75)
            iqr = q3 - q1
            lower_bound = max(1, q1 - 1.5 * iqr)
            upper_bound = q3 + 1.5 * iqr

            filtered_distances = distances[
                (distances >= lower_bound) & (distances <= upper_bound)
                ]
        else:
            filtered_distances = distances

        if len(filtered_distances) == 0:
            return -1

        return np.median(filtered_distances)

    except Exception:
        return -1


def _visualize_grid_detection(image, small_grid_size, large_grid_size, debug_dir):
    height, width = image.shape
    grid_overlay = cv2.cvtColor(image.copy(), cv2.COLOR_GRAY2BGR)

    small_grid_int = max(1, int(small_grid_size))
    for y in range(0, height, small_grid_int):
        cv2.line(grid_overlay, (0, y), (width, y), (0, 255, 0), 1)

    for x in range(0, width, small_grid_int):
        cv2.line(grid_overlay, (x, 0), (x, height), (0, 255, 0), 1)

    large_grid_int = max(5, int(large_grid_size))
    for y in range(0, height, large_grid_int):
        cv2.line(grid_overlay, (0, y), (width, y), (0, 0, 255), 2)

    for x in range(0, width, large_grid_int):
        cv2.line(grid_overlay, (x, 0), (x, height), (0, 0, 255), 2)

    plt.figure(figsize=(12, 8))
    plt.imshow(grid_overlay)
    plt.title("Detected Grid Overlay")
    plt.savefig(f"{debug_dir}/grid_detection.png")
    plt.close()


def calibrate_signal(x_values, y_values, small_grid_size, time_per_grid=0.04, mv_per_grid=0.1):
    time_values = [x * (time_per_grid / small_grid_size) for x in x_values]
    amplitude_values = [y * (mv_per_grid / small_grid_size) for y in y_values]

    amplitude_values = _correct_baseline(amplitude_values)

    return time_values, amplitude_values


def _correct_baseline(amplitude_values):
    if not amplitude_values:
        return amplitude_values

    hist, bin_edges = np.histogram(amplitude_values, bins=50)
    most_common_bin = np.argmax(hist)
    baseline_estimate1 = (bin_edges[most_common_bin] + bin_edges[most_common_bin + 1]) / 2

    amplitude_array = np.array(amplitude_values)
    derivatives = np.abs(np.diff(amplitude_array))
    flat_threshold = np.percentile(derivatives, 30)
    flat_segments = derivatives < flat_threshold

    if np.sum(flat_segments) > len(amplitude_values) * 0.1:
        baseline_estimate2 = np.mean(amplitude_array[:-1][flat_segments])
    else:
        baseline_estimate2 = np.median(amplitude_values)

    baseline = 0.4 * baseline_estimate1 + 0.6 * baseline_estimate2

    return [a - baseline for a in amplitude_values]


def resample_signal(time_values, amplitude_values, target_sample_rate):
    duration = time_values[-1] - time_values[0]

    num_samples = int(duration * target_sample_rate)

    f = interpolate.interp1d(
        time_values, amplitude_values,
        kind='linear', bounds_error=False, fill_value='extrapolate'
    )

    new_time_values = np.linspace(time_values[0], time_values[-1], num_samples)

    new_amplitude_values = f(new_time_values)

    return new_time_values, new_amplitude_values