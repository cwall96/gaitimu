import pandas as pd
import numpy as np
import math
from scipy.signal import find_peaks
def cadence_v2(acc_x, acc_y, acc_z):
    smooth_rate = 10

    percentagecutoff = round(len(acc_x) * 0.05)

    # Smooth arrays with smooth_rate
    smoothed_acc_x = pd.DataFrame(acc_x).rolling(smooth_rate).mean().values[percentagecutoff:-percentagecutoff]
    smoothed_acc_y = pd.DataFrame(acc_y).rolling(smooth_rate).mean().values[percentagecutoff:-percentagecutoff]
    smoothed_acc_z = pd.DataFrame(acc_z).rolling(smooth_rate).mean().values[percentagecutoff:-percentagecutoff]

    # Set null values to 2 (arbitrary)
    smoothed_acc_x[np.isnan(smoothed_acc_x)] = 0.1
    smoothed_acc_y[np.isnan(smoothed_acc_y)] = 0.1
    smoothed_acc_z[np.isnan(smoothed_acc_z)] = 0.1

    # Calculate RMS
    compound_smoothed_acc = [math.sqrt(smoothed_acc_y[i] ** 2) for i in range(len(smoothed_acc_x))]

    # Get min, max, and average - set threshold based on values
    max_val = max(compound_smoothed_acc)
    main_peak_threshold = max_val * 0.7

    # Find main peaks on RMS signal above threshold with a minimum distance of 15
    main_peaks = find_peaks(compound_smoothed_acc, height=main_peak_threshold, distance=38)[0]

    # Extract basic outcomes
    main_peaks_count = len(main_peaks)


    average_time_between_steps = []
    for i in range(len(main_peaks) - 1):
        step = main_peaks[i]
        next_step = main_peaks[i+1]
        distance_between_steps = next_step - step
        average_time_between_steps.append(distance_between_steps)

    average_step_time_hz = sum(average_time_between_steps) / len(average_time_between_steps)
    average_step_time_s = average_step_time_hz / 100
    bpm = 60 / average_step_time_s

    return { "success": True, "steps": main_peaks_count, "bpm" : bpm, "step_time":average_step_time_s }