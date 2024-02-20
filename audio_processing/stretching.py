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
import io
import subprocess


OUTPUT_DIR = "./output_audio_files"
RAW_AUDIO_DIR = "./raw_audio_files" 

# Ensure the output directory exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def fetch_audio_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return io.BytesIO(response.content)
    else:
        print("Failed to download the audio.")
        return None

def estimate_bpm(audio_segment, duration=30):
    # Take a sample of the audio for BPM estimation
    start_sample = max(0, (len(audio_segment) - duration * 1000) // 2)
    sample_segment = audio_segment[start_sample:start_sample + duration * 1000]

    samples = np.array(sample_segment.get_array_of_samples())
    if sample_segment.channels == 2:
        samples = samples.reshape((-1, 2))
    y = samples.mean(axis=1) if sample_segment.channels > 1 else samples
    sr = sample_segment.frame_rate

    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
    print(f"Estimated original BPM: {tempo}")
    return tempo

def change_bpm_audiosegment(audio_file_path, target_bpm, original_bpm):
    factor = float(original_bpm) / float(target_bpm)
    speed_change = 1 / factor

    output_uuid = str(uuid.uuid1())
    output_file = os.path.join(OUTPUT_DIR, f"{output_uuid}.mp3")

    # Using the file path directly with ffmpeg
    subprocess.call(['ffmpeg', '-i', audio_file_path, '-filter:a', f"atempo={speed_change}", '-ab', '128k', output_file])

    return output_file


def process_audio_files(filepath, target_bpm):
    audio_file_path = os.path.join(RAW_AUDIO_DIR, filepath)
    print(audio_file_path)


    if os.path.exists(audio_file_path):
        audio_segment = AudioSegment.from_file(audio_file_path, format="mp3")

        # Check if filepath is '100.mp3' and set original_bpm to 100
        if filepath == '100.mp3':
            original_bpm = 100
        else:
            original_bpm = estimate_bpm(audio_segment)

        output_file = change_bpm_audiosegment(audio_file_path, target_bpm, original_bpm)
        return output_file.split("/")[-1]
    else:
        print(f"File {filepath} not found in {RAW_AUDIO_DIR}.")
        return None