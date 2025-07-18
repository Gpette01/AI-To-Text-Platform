import torchaudio
import soundfile as sf
import sys
import os
import time
import threading
import random
import tempfile
import subprocess
from stop_flag import transcription_stop_flag as stop_flag
from faster_whisper import WhisperModel
import numpy as np
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Retrieve the threshold from the .env file, with a default value of 0.1
THRESHOLD = float(os.getenv("SILENCE_THRESHOLD", 0.1))

# Db connection
# import sys
# from pathlib import Path

# Add the parent directory to sys.path to allow imports from sibling directories
# sys.path.append(str(Path(__file__).resolve().parent.parent / "db"))

# Import the connect.py module
from db import connect

def defineModel():
    model_size = "distil-large-v3"
    return WhisperModel(model_size, device="cpu", compute_type="int8")

def read_new_audio(file, last_position):
    try:
        
        # Load the audio from last_position onwards
        new_data, sample_rate = torchaudio.load(file, frame_offset=last_position, num_frames=-1)
        # Save the number of frames read
        frames_read = new_data.size(1)  # Get the number of frames read from the audio file
        # Check if no new frames were read (end of file)
        if frames_read == 0:
            return None, last_position, 0.0
        # Calculate the time offset before resampling
        time_offset = last_position / sample_rate  # Time offset in seconds
        # Resample the audio to 16kHz
        new_data = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)(new_data)
        # Convert the audio to mono by averaging channels
        new_data = new_data.mean(dim=0, keepdim=True)  # Convert to mono
        # Squeeze and check for scalar
        new_data = new_data.squeeze()
        if new_data.dim() == 0:  # Scalar
            print("new_data is a scalar, returning empty array.")
            return None, last_position, 0.0
        # Calculate new position
        new_position = last_position + frames_read
        return new_data.numpy(), new_position, time_offset  # Return time_offset
        
    except RuntimeError as e:
        print(f"Error reading new audio: {e}")
        return None, last_position, 0.0


import matplotlib.pyplot as plt
import pickle



def transcribe_audio(wavFile, model, identifier):
    last_position = 0
    conn = connect.connect_to_database()
    print(f"FILE IS: {wavFile}")
    try:
        while not stop_flag.is_set():
            if wavFile and os.path.exists(wavFile):
                new_data, last_position, time_offset = read_new_audio(wavFile, last_position)
                # print(f"Last position: {last_position}, Time offset: {time_offset}")
                if new_data is not None and len(new_data) > 0:
                    # Transcribe the new audio data
                    segments, info = model.transcribe(new_data, beam_size=5, word_timestamps=True)
                    
                    for segment in segments:
                        # Adjust timestamps by adding the time offset
                        adjusted_start = segment.start + time_offset
                        adjusted_end = segment.end + time_offset
                        # print(f"[{adjusted_start:.2f}s -> {adjusted_end:.2f}s] {segment.text}")
                        text_copy = segment.text[:]  # or str(segment.text)
                        identifier.process_transcription(conn, adjusted_start, adjusted_end, wavFile, text_copy)
                        connect.insert_transcription(conn, adjusted_start, adjusted_end, text_copy, wavFile)
                else:
                    print("No new data to transcribe.")

            else:
                print("File does not exist.")
            time.sleep(1)  # Wait for 1 second before reading new data
    except KeyboardInterrupt:
        print("Transcription stopped by user")
    finally:
        print("Transcription finished")


def print_transcription(transcription_file):
    print("File: ", transcription_file, flush=True)
    last_size = 0
    
    try:
        with open(transcription_file, "r") as f:
            while True:
                if os.path.exists(transcription_file):
                    current_size = os.path.getsize(transcription_file)
                    if current_size > last_size:
                        f.seek(last_size)
                        new_lines = f.read()
                        if new_lines:
                            words = new_lines.split()
                            for word in words:
                                print(word, end=" ", flush=True)
                                f.flush()
                                time.sleep(random.uniform(0.1, 0.5))  # Random wait between 0.1 and 0.5 seconds
                    last_size = current_size
                
                time.sleep(5)  # Check for changes every second
    except KeyboardInterrupt:
        print("Printing stopped by user")
    finally:
        # f.close()
        print("Printing finished")

def is_silence(data, threshold=THRESHOLD):
    return np.max(np.abs(data)) < threshold

# def checkForSilence(file, plot_stop_flag, last_position, seconds=5):
#     sample_rate = 16000  # Assuming the audio is resampled to 16kHz
#     print(f"File is: {file} last position is: {last_position}")
#     silence_duration = 0

#     while silence_duration < seconds and not plot_stop_flag.is_set():
#         new_data, last_position, timeOffset = read_new_audio(file, last_position)
#         if new_data is None:
#             # No new data; wait before trying again
#             time.sleep(1)
#             continue

#         # Calculate the duration of the new data in seconds
#         duration = len(new_data) / sample_rate

#         # Check if the audio data represents silence
#         if is_silence(new_data):
#             silence_duration += duration
#         else:
#             silence_duration = 0  # Reset if sound is detected

#         # Add a sleep to allow time for new data
#         time.sleep(1)

#     if silence_duration >= seconds:
#         print(f"Silence detected for {seconds} seconds.")
#         return last_position
def checkForSilence(file, plot_stop_flag, last_position, seconds=5, skip_duration=0):
    """
    Scan the WAV file (starting from last_position) looking for at least `seconds`
    of silence. If a skip_duration is provided, that many seconds of silence at the
    beginning will be ignored (not counted) to avoid false triggers from intentionally
    inserted silence.
    
    Returns the updated last_position if silence is detected.
    """
    sample_rate = 16000  # Assuming the audio is resampled to 16kHz
    print(f"File is: {file} starting at last_position: {last_position}")
    silence_duration = 0.0
    skip_remaining = skip_duration  # seconds to ignore
    
    while silence_duration < seconds and not plot_stop_flag.is_set():
        new_data, last_position, timeOffset = read_new_audio(file, last_position)
        if new_data is None:
            # No new data; wait before trying again
            time.sleep(1)
            continue

        # Calculate the duration of the new data in seconds.
        duration = len(new_data) / sample_rate

        # If we have a skip period, subtract from it and do not count this audio.
        if skip_remaining > 0:
            skip_remaining -= duration
            # Optionally, you might reset silence_duration here
            # in case you want to fully ignore this chunk.
            silence_duration = 0
        else:
            # Check if the audio data represents silence.
            if is_silence(new_data):
                silence_duration += duration
            else:
                silence_duration = 0  # Reset if sound is detected

        # Allow time for new data to accumulate.
        time.sleep(1)

    if silence_duration >= seconds:
        print(f"Silence detected for {seconds} seconds.")
        return last_position


    
        
if __name__ == "__main__":
    file = "/app/models/HARVARD_rawcopy/Harvard_list_01.wav"
    # conn = connect.connect_to_database()
    model = defineModel()
    
    # print(checkForSilence(file, seconds=1))
    # transcription_file = "transcription.txt"
    
    # with open(transcription_file, "w") as f:
    #     pass
        
    # last_position = 0
    
    transcription_thread = threading.Thread(target=transcribe_audio, args=(file, model))
    transcription_thread.start()
    
    # print_transcription_thread = threading.Thread(target=print_transcription, args=(transcription_file,))
    # print_transcription_thread.start()
    
    transcription_thread.join()
    # print_transcription_thread.join()
