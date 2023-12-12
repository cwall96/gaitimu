import os
import requests
import librosa
import numpy as np
import soundfile as sf
import pyrubberband as pyrb
import time
from audiostretchy.stretch import stretch_audio
from urllib.parse import urljoin,urlparse
from pydub import AudioSegment
import uuid


OUTPUT_DIR = "output_audio_files"

# Ensure the output directory exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

TMP_DIR = "/tmp"  # directory for temporary files
if not os.path.exists(TMP_DIR):
    os.makedirs(TMP_DIR)


def ensure_temp_deleted(file_path):
    """Utility function to ensure that temporary files are deleted."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Error deleting temp file: {e}")


def estimate_bpm(input_file):
    y, sr = librosa.load(input_file, sr=None)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
    print(f"Estimated original BPM: {tempo}")

    return tempo


def change_bpm_audiostretchy(input_file, target_bpm, original_bpm):
    # Generate UUIDs for temporary and output files
    temp_uuid = str(uuid.uuid1())
    output_uuid = str(uuid.uuid1())

    temp_path = f"{TMP_DIR}/{temp_uuid}.wav"
    output_file = f"{OUTPUT_DIR}/{output_uuid}.mp3"

    print(f"Temporary file: {temp_path}")
    print(f"Output file: {output_file}")

    try:
        factor = float(original_bpm) / float(target_bpm)
    except TypeError:
        print("Invalid BPM values. Make sure they are numeric.")
        return None

    print("Changing BPM with AudioStretchy...")
    start_time = time.time()

    try:
        # Load and process the audio
        y, sr = librosa.load(input_file, sr=None, res_type='kaiser_best')
        sf.write(temp_path, y, sr)

        # Stretch the audio
        stretch_audio(temp_path, temp_path, ratio=factor)

        # Convert WAV to MP3
        audio = AudioSegment.from_wav(temp_path)
        audio.export(output_file, format="mp3")  # Export as MP3

        ensure_temp_deleted(temp_path)

        elapsed_time = time.time() - start_time
        print(f"BPM change completed in {elapsed_time:.2f} seconds!")

        return output_file

    except Exception as e:
        print(f"Error processing the audio with AudioStretchy: {e}")
        ensure_temp_deleted(temp_path)
        return None


def process_audio_files(filepath, target_bpm):

    temp_path = os.path.join(TMP_DIR, "tempotemp.mp3")

    filepath = f"raw_audio_files/{filepath}"

    original_bpm = estimate_bpm(filepath)

    as_output_file = change_bpm_audiostretchy(filepath, target_bpm, original_bpm)
    
    # Purge tmp directory
    ensure_temp_deleted(temp_path)

    return as_output_file.split("/")[-1]