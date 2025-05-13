import os
import numpy as np
import wfdb

def save_to_wfdb(amplitude_values, sample_rate, output_dir, base_filename):
    signal = np.array(amplitude_values).reshape(-1, 1)

    # Define the channel information
    channel_names = ['ECG I']
    units = ['mV']

    # ADC information
    adc_gain = 1000.0
    baseline = 0 

    # Checking output dir
    os.makedirs(output_dir, exist_ok=True)
    record_name = base_filename

    # Save record
    wfdb.wrsamp(
        record_name=record_name,
        fs=sample_rate,
        units=units,
        sig_name=channel_names,
        p_signal=signal,
        fmt=['16'],
        adc_gain=[adc_gain],
        baseline=[baseline],
        comments=[f'Digitized from ECG image: {base_filename}'],
        write_dir=output_dir
    )

    # Return path
    return os.path.join(output_dir, record_name)
