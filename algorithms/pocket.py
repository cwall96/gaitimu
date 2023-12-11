import math
import numpy as np
from scipy.signal import butter, filtfilt, find_peaks

def pocket(acc_x, acc_y, acc_z):
    def butter_lowpass_filter(data, cutoff, fs, order):
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        y = filtfilt(b, a, data)
        return y

    filtered_acc_x = butter_lowpass_filter(acc_x, 10, 100, 3)
    filtered_acc_y = butter_lowpass_filter(acc_y, 10, 100, 3)
    filtered_acc_z = butter_lowpass_filter(acc_z, 10, 100, 3)

    # Exclude the first 10% of the filtered data
    filtered_acc_x = filtered_acc_x[int(len(filtered_acc_x) * 0.001):]
    filtered_acc_y = filtered_acc_y[int(len(filtered_acc_y) * 0.001):]
    filtered_acc_z = filtered_acc_z[int(len(filtered_acc_z) * 0.001):]

    # Calculate RMS
    compound_smoothed_acc = np.array([math.sqrt(filtered_acc_x[i] ** 2 + filtered_acc_y[i] ** 2 + filtered_acc_z[i] ** 2) for i in range(len(filtered_acc_x))])

    # Find main peaks on RMS signal
    max_val = max(compound_smoothed_acc)
    main_peak_threshold = max_val * 0.6
    main_peaks = find_peaks(compound_smoothed_acc, height=main_peak_threshold, distance=80)[0]

    # Calculate time intervals between successive strides
    stride_intervals = []
    sampling_rate = 100 # Adjust this according to your data's sampling rate

    for i in range(len(main_peaks) - 1):
        time_interval = (main_peaks[i+1] - main_peaks[i]) / sampling_rate  # Convert to seconds
        stride_intervals.append(time_interval)

    average_stride_time_s = sum(stride_intervals) / len(stride_intervals)
    average_step_time_s = average_stride_time_s / 2
    bpm = 60 / average_step_time_s


    # Calculate cadence
    stride_count = len(main_peaks)
    cadence = stride_count * 2  # Double the stride count for cadence

    return { "success": True, "steps": cadence, "bpm" : bpm, "step_time":average_step_time_s }