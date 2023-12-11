import os
import requests
import librosa
import numpy as np
import soundfile as sf
import pyrubberband as pyrb
import time
from audiostretchy.stretch import stretch_audio
from urllib.parse import urljoin,urlparse
from pydub import AudioSegment  # Import pydub

OUTPUT_DIR = "timestretchingoutput"

# Ensure the output directory exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

TMP_DIR = "/tmp"  # directory for temporary files

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
    return tempo

def fetch_mp3_from_github(url, save_path):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    downloaded_size = 0

    if response.status_code == 200:
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                downloaded_size += len(chunk)
                f.write(chunk)
                progress = (downloaded_size / total_size) * 100
                print(f"Downloading: {progress:.2f}% complete", end='\r')
        print("\nDownload completed!")
        return save_path
    else:
        print("Failed to download the MP3.")
        return None
def change_bpm_audiostretchy(input_file, target_bpm, original_bpm, github_url):
    url_path = urlparse(github_url).path
    github_file_name = os.path.splitext(os.path.basename(url_path))[0]

    file_specific_output_dir = os.path.join(OUTPUT_DIR, github_file_name)
    if not os.path.exists(file_specific_output_dir):
        os.makedirs(file_specific_output_dir)

    temp_path = os.path.join(TMP_DIR, "temp_audio_file.wav")
    
    print("Changing BPM with AudioStretchy...")
    start_time = time.time()

    try:
        factor = original_bpm / target_bpm
        y, sr = librosa.load(input_file, sr=None, res_type='kaiser_best')

        sf.write(temp_path, y, sr)

        # Modify the output file name to include the folder name and target BPM, but before appending the file extension
        output_file_name = f"{github_file_name}_{target_bpm}"

        # Stretch the audio
        stretch_audio(temp_path, temp_path, ratio=factor)

        # Remove '_novocals' from the file name if it exists, after stretching
        output_file_name = output_file_name.replace('_novocals', '')

        # Now add the correct file extension
        output_file_name += ".mp3"
        output_file = os.path.join(file_specific_output_dir, output_file_name)

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

def list_files_in_github_directory(github_dir_url):
    # Assuming the URL format is https://github.com/[username]/[repo]/raw/main/[path]/
    api_url = github_dir_url.replace('https://github.com/', 'https://api.github.com/repos/')
    api_url = api_url.replace('/raw/main/', '/contents/')
    response = requests.get(api_url)
    if response.status_code == 200:
        return [file['name'] for file in response.json() if file['name'].endswith('.mp3')]
    else:
        print("Failed to fetch file list from GitHub.")
        return []

def process_audio_files(github_dir_url):
    files = list_files_in_github_directory(github_dir_url)

    if files:
        print("Select a file to download:")
        for i, file in enumerate(files):
            print(f"{i + 1}. {file}")
        file_choice = int(input("Enter the number of the file: ")) - 1
        selected_file = files[file_choice]
        selected_file_url = urljoin(github_dir_url, selected_file)

        temp_path = os.path.join(TMP_DIR, "tempotemp.mp3")
        downloaded_file = fetch_mp3_from_github(selected_file_url, temp_path)

        original_bpm = estimate_bpm(downloaded_file)
        print(f"Estimated original BPM: {original_bpm}")

        for target_bpm in range(80, 131):
            as_output_file = change_bpm_audiostretchy(downloaded_file, target_bpm, original_bpm, selected_file_url)
            if as_output_file:
                print(f"File saved as {as_output_file}")

        ensure_temp_deleted(temp_path)
    else:
        print("No files found in the specified GitHub directory.")