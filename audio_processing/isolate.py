from spleeter.separator import Separator
import os
from pydub import AudioSegment
import glob

def remove_vocals(input_path, output_path):
    # Using the 2stems model to separate vocals and accompaniment
    separator = Separator('spleeter:2stems')
    
    # Temporary output directory
    temp_output_dir = "novocals_temp"
    separator.separate_to_file(input_path, temp_output_dir)
    
    # Locate the accompaniment WAV file
    accompaniment_wav_files = glob.glob(os.path.join(temp_output_dir, "SA", "accompaniment.Codec.WAV"), recursive=True)
    
    if accompaniment_wav_files:
        accompaniment_wav_path = accompaniment_wav_files[0]  # Take the first file found
        audio = AudioSegment.from_wav(accompaniment_wav_path)
        audio.export(output_path, format="mp3")
        print(f"Processed {input_path} and saved as {output_path}")
    else:
        print("Accompaniment file not found!")

if __name__ == "__main__":
    input_directory = "removerinput"
    output_directory = "removeroutput"
    os.makedirs(output_directory, exist_ok=True)

    # List files in the input directory
    files = os.listdir(input_directory)
    print("Available files:")
    for index, file in enumerate(files):
        print(f"{index + 1}: {file}")

    # Get user selection
    file_index = int(input("Select a file by number: ")) - 1
    file_name = files[file_index]

    # Process the selected file
    input_file_path = os.path.join(input_directory, file_name)
    output_file_name = os.path.splitext(file_name)[0] + '_novocals.mp3'
    output_file_path = os.path.join(output_directory, output_file_name)

    remove_vocals(input_file_path, output_file_path)
