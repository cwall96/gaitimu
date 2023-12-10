from flask import Flask, request, jsonify
import pandas as pd
from flask_cors import CORS
import math
import numpy as np
import statistics
from scipy import interpolate
from scipy.signal import butter, filtfilt, find_peaks

app = Flask(__name__)
CORS(app)

SAVE_FILES = True

@app.route("/gait", methods=["POST"])
def run():
    # Extract columns to array
    acc_x = request.json["xVals"]
    acc_y = request.json["yVals"]
    acc_z = request.json["zVals"]
    test_name = request.json["testName"]

    t_vals = request.json["timeVals"]

    df = pd.DataFrame({"x": acc_x, "y": acc_y, "z": acc_z, "T": t_vals})

    df.to_csv(f"/home/cwall96/csvs/{test_name}.csv")

    smooth_rate = 3

    percentagecutoff = round(len(acc_x) * 0.15)

    # Smooth arrays with smooth_rate
    smoothed_acc_x = pd.DataFrame(acc_x).rolling(smooth_rate).mean().values[percentagecutoff:-percentagecutoff]
    smoothed_acc_y = pd.DataFrame(acc_y).rolling(smooth_rate).mean().values[percentagecutoff:-percentagecutoff]
    smoothed_acc_z = pd.DataFrame(acc_z).rolling(smooth_rate).mean().values[percentagecutoff:-percentagecutoff]

    # Set null values to 5 (arbitrary)
    smoothed_acc_x[np.isnan(smoothed_acc_x)] = 2
    smoothed_acc_y[np.isnan(smoothed_acc_y)] = 2
    smoothed_acc_z[np.isnan(smoothed_acc_z)] = 2

    # Calculate RMS
    compound_smoothed_acc = [math.sqrt(smoothed_acc_x[i] ** 2 + smoothed_acc_y[i] ** 2 + smoothed_acc_z[i] ** 2) for i in range(len(smoothed_acc_x))]

    # Get min, max and average - set threshold based on values
    max_val = max(compound_smoothed_acc)

    threshold = max_val*0.6

    # Find peaks on RMS signal above threshold with a minimum distance of 30
    peaks = find_peaks(compound_smoothed_acc, height=threshold, distance=38)[0]

    average_time_between_steps = []
    for i in range(len(peaks) - 1):
      step = peaks[i]
      next_step = peaks[i+1]
      distance_between_steps = next_step - step
      average_time_between_steps.append(distance_between_steps)

    average_step_time_hz = sum(average_time_between_steps)/len(average_time_between_steps)
    average_step_time_s = average_step_time_hz/100
    bpm = 60/average_step_time_s

    return jsonify({ "success": True, "steps": len(peaks), "bpm" : bpm, "step_time":average_step_time_s })

@app.route("/cadence", methods=["POST"])
def runcadence():
    # Extract columns to array
    acc_x = request.json["xVals"]
    acc_y = request.json["yVals"]
    acc_z = request.json["zVals"]
    test_name = request.json["testName"]

    t_vals = request.json["timeVals"]

    df = pd.DataFrame({"x": acc_x, "y": acc_y, "z": acc_z, "T": t_vals})

    df.to_csv(f"/home/cwall96/csvs/{test_name}.csv")

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

    return jsonify({ "success": True, "steps": main_peaks_count, "bpm" : bpm, "step_time":average_step_time_s })


@app.route("/pocket", methods=["POST"])
def pocket():
    # Extract columns to array
    acc_x = request.json["xVals"]
    acc_y = request.json["yVals"]
    acc_z = request.json["zVals"]
    test_name = request.json["testName"]

    t_vals = request.json["timeVals"]

    df = pd.DataFrame({"x": acc_x, "y": acc_y, "z": acc_z, "T": t_vals})

    df.to_csv(f"/home/cwall96/csvs/{test_name}.csv")

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

    return jsonify({ "success": True, "steps": cadence, "bpm" : bpm, "step_time":average_step_time_s })
