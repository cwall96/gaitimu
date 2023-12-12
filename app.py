# Lib imports
from flask import Flask, request, jsonify
import pandas as pd
from flask_cors import CORS

# Utilities for validating and extracting data from the request
from utils.validate_request_params import validate_request_params
from utils.extract_data import extract_data

# Algorithm imports
from algorithms.cadence_v1 import cadence_v1
from algorithms.cadence_v2 import cadence_v2
from algorithms.pocket import pocket

# Audio processing imports
from audio_processing.stretching import process_audio_files

# Define flask app
app = Flask(__name__)
CORS(app)

# Define routes
@app.route("/calculate/<algorithm>", methods=["POST"])
def calculate_gait_outcome(algorithm):
    validation_check = validate_request_params(request)
    if not validation_check["success"]:
        return jsonify(validation_check)
    
    df, acc_x, acc_y, acc_z = extract_data(request)

    result = {}

    if algorithm == "cadence_v1":
        result = cadence_v1(acc_x, acc_y, acc_z)
    if algorithm == "cadence_v2":
        result = cadence_v2(acc_x, acc_y, acc_z)
    if algorithm == "pocket":
        result = pocket(acc_x, acc_y, acc_z)
    
    return jsonify(result)

@app.route("/stretch", methods=["GET"])
def stretch_audio_file():
    song_filename = request.args.get("song_filename")
    bpm = request.args.get("bpm")
    isolate_vocals = request.args.get("isolate_vocals")

    output_audio_filepath = process_audio_files(song_filename, bpm)

    return jsonify({ "success": True, "output_path": output_audio_filepath })
