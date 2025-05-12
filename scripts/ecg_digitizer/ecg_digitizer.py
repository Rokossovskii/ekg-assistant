#!/usr/bin/env python3
"""
Single-Lead ECG Image to WFDB Converter

This script converts single-lead ECG images to WFDB format.
The converter automatically detects the grid in the image to scale
the signal properly in millivolts (amplitude) and seconds (time).

Usage:
    python main.py <input_image> <output_directory> [options]

Options:
    --time-per-grid SECONDS   Time per small grid square (default: 0.04s)
    --mv-per-grid MV          Voltage per small grid square (default: 0.1mV)
    --sample-rate RATE        Force specific sample rate (default: calculated from grid)
    --debug                   Enable debug mode with additional output
"""

import argparse
import os
import sys
from modules.ecg_processor import ECGProcessor


def parse_arguments():
    parser = argparse.ArgumentParser(description='Convert ECG images to WFDB format')

    # Required arguments
    parser.add_argument('input_image', help='Path to the input ECG image')
    parser.add_argument('output_dir', help='Directory to save output files')

    # Optional arguments
    parser.add_argument('--time-per-grid', type=float, default=0.04,
                      help='Time per small grid square in seconds (default: 0.04s)')
    parser.add_argument('--mv-per-grid', type=float, default=0.1,
                      help='Voltage per small grid square in mV (default: 0.1mV)')
    parser.add_argument('--sample-rate', type=int,
                      help='Force specific sample rate (default: calculated from grid)')
    parser.add_argument('--debug', action='store_true',
                      help='Enable debug mode with additional output')

    return parser.parse_args()


def main():
    args = parse_arguments()
    os.makedirs(args.output_dir, exist_ok=True)

    try:
        processor = ECGProcessor(
            debug=args.debug,
            time_per_grid=args.time_per_grid,
            mv_per_grid=args.mv_per_grid,
            force_sample_rate=args.sample_rate
        )

        time_values, amplitude_values, sample_rate = processor.process(
            args.input_image, args.output_dir
        )

        print(f"Processing completed successfully. Output saved to {args.output_dir}")
        print(f"Signal duration: {time_values[-1] - time_values[0]:.2f} seconds")
        print(f"Amplitude range: {min(amplitude_values):.2f} to {max(amplitude_values):.2f} mV")
        print(f"Sample rate: {sample_rate} Hz")
        print(f"Total samples: {len(time_values)}")
        print(f"Calibration: {args.time_per_grid}s and {args.mv_per_grid}mV per small grid")

    except Exception as e:
        print(f"Error processing ECG image: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()