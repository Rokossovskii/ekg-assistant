import os
from pathlib import Path

import matplotlib.pyplot as plt

from .image_processing import preprocess_image
from .signal_processing import (
    calibrate_signal,
    detect_grid_size,
    extract_signal,
    resample_signal,
)
from .wfdb_utils import save_to_wfdb


class ECGProcessor:
    def __init__(
        self, debug=False, time_per_grid=0.04, mv_per_grid=0.1, force_sample_rate=None
    ):
        self.debug = debug
        self.time_per_grid = time_per_grid
        self.mv_per_grid = mv_per_grid
        self.force_sample_rate = force_sample_rate

    def process(self, image_path, output_dir):
        debug_dir = self._setup_directories(output_dir)

        binary_image, original_image = preprocess_image(image_path, debug_dir)

        small_grid_size = self._detect_grid(original_image, debug_dir)

        x_values, y_values = extract_signal(binary_image, debug_dir)

        sample_rate, time_values, amplitude_values = self._calibrate(
            x_values, y_values, small_grid_size
        )

        self._generate_outputs(
            time_values, amplitude_values, sample_rate, output_dir, image_path
        )

        return time_values, amplitude_values, sample_rate

    def process_to_wfdb(self, image_path, tmpdir) -> list[dict]:
        binary_image, original_image = preprocess_image(image_path)

        small_grid_size = self._detect_grid(original_image)

        x_values, y_values = extract_signal(binary_image)

        sample_rate, _, amplitude_values = self._calibrate(
            x_values, y_values, small_grid_size
        )

        base_filename = os.path.splitext(os.path.basename(image_path))[0]

        wfdb_path = save_to_wfdb(amplitude_values, sample_rate, tmpdir, base_filename)

        # wfdb_dict = convert_wfdb_to_dict(tmp_dat_path=wfdb_path)
        print(f"Saved WFDB record: {wfdb_path}")
        wfdb_path = Path(wfdb_path)
        return wfdb_path

    def _setup_directories(self, output_dir):
        os.makedirs(output_dir, exist_ok=True)

        debug_dir = None
        if self.debug:
            debug_dir = os.path.join(output_dir, "debug")
            os.makedirs(debug_dir, exist_ok=True)

        return debug_dir

    def _detect_grid(self, image, debug_dir=None):
        small_grid_size, large_grid_size = detect_grid_size(image, debug_dir)

        if self.debug:
            print(
                f"Detected grid sizes - Small: {small_grid_size:.2f} pixels, "
                f"Large: {large_grid_size:.2f} pixels"
            )

        return small_grid_size

    def _calibrate(self, x_values, y_values, grid_size):
        if self.force_sample_rate:
            sample_rate = self.force_sample_rate
        else:
            sample_rate = self._calculate_sample_rate(grid_size)

        time_values, amplitude_values = calibrate_signal(
            x_values, y_values, grid_size, self.time_per_grid, self.mv_per_grid
        )

        if len(time_values) > 0:
            current_rate = len(time_values) / (time_values[-1] - time_values[0])
            if abs(current_rate - sample_rate) / sample_rate > 0.05:
                time_values, amplitude_values = resample_signal(
                    time_values, amplitude_values, sample_rate
                )

        return sample_rate, time_values, amplitude_values

    def _calculate_sample_rate(self, grid_size):
        sample_rate = int(round(grid_size / self.time_per_grid))

        # Ensure reasonable limits (125Hz to 1000Hz)
        sample_rate = max(125, min(1000, sample_rate))

        if self.debug:
            print(f"Using sample rate: {sample_rate} Hz")

        return sample_rate

    def _generate_outputs(
        self, time_values, amplitude_values, sample_rate, output_dir, image_path
    ):
        self._create_plot(time_values, amplitude_values, output_dir)

        base_filename = os.path.splitext(os.path.basename(image_path))[0]

        wfdb_path = save_to_wfdb(
            amplitude_values, sample_rate, output_dir, base_filename
        )

        if self.debug:
            print(f"Saved WFDB record: {wfdb_path}")

    def _create_plot(self, time_values, amplitude_values, output_dir):
        plt.figure(figsize=(12, 6))
        plt.plot(time_values, amplitude_values, "b-", linewidth=1)
        plt.title("Calibrated ECG Signal")

        plt.grid(
            True, which="major", linestyle="-", linewidth=0.8, color="pink", alpha=0.7
        )
        plt.grid(
            True, which="minor", linestyle=":", linewidth=0.5, color="pink", alpha=0.5
        )

        plt.axhline(y=0, color="r", linestyle="-", alpha=0.3)

        plt.savefig(os.path.join(output_dir, "ecg_plot.png"), dpi=300)
        plt.close()

        plt.savefig(os.path.join(output_dir, "ecg_plot.png"), dpi=300)
        plt.close()
        plt.close()
