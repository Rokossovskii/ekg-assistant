import os
import numpy as np


def save_to_wfdb(amplitude_values, sample_rate, output_dir, base_filename):
    try:
        import wfdb
    except ImportError:
        raise ImportError("wfdb package is required. Install with: pip install wfdb")

    record_name = os.path.join(output_dir, base_filename)
    signal = np.array(amplitude_values).reshape(-1, 1)

    # Define the channel information
    channel_names = ['ECG I']
    units = ['mV']

    # ADC information
    adc_gain = 1000.0  # 1000 ADC units per mV
    baseline = 0  # Baseline at 0

    # Save the record
    wfdb.wrsamp(
        record_name=record_name,
        fs=sample_rate,
        units=units,
        sig_name=channel_names,
        p_signal=signal,
        fmt=['16'],  # 16-bit format
        adc_gain=[adc_gain],
        baseline=[baseline],
        comments=[f'Digitized from ECG image: {base_filename}']
    )

    return record_name
