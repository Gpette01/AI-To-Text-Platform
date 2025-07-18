import os
import time
import re
import jiwer
import subprocess
import pandas as pd
from pydub import AudioSegment

# Path to the directory with .wav files
audio_directory = "HARVARD_raw"
whisper_cpp_path = "../../whisper.cpp/main"  # Path to the whisper.cpp executable
model_path = "../../whisper.cpp/models/ggml-large-v3-turbo.bin"  # Path to the large-v3-turbo model file
temp_audio_path = "temp_audio_16kHz_16bit.wav"  # Temporary file to hold 16kHz, 16-bit audio

# Load and process ground truth sentences
ground_truth_dict = {}
with open("harvsents.txt", "r") as f:
    current_group = None
    for line in f:
        group_match = re.match(r"H(\d+)", line)
        sentence_match = re.match(r"\s*(\d+)\.\s+(.*)", line)

        if group_match:
            current_group = group_match.group(1).zfill(2)
        elif sentence_match and current_group:
            sentence_text = sentence_match.group(2).strip()
            key = f"H{current_group}"
            if key in ground_truth_dict:
                ground_truth_dict[key].append(sentence_text)
            else:
                ground_truth_dict[key] = ["Harvard list number " + str(int(current_group))]
                ground_truth_dict[key].append(sentence_text)

# Function to get evaluation metrics
def evaluate_transcription(reference, hypothesis):
    wer = jiwer.wer(reference, hypothesis)
    mer = jiwer.mer(reference, hypothesis)
    wil = jiwer.wil(reference, hypothesis)
    return {"WER": wer, "MER": mer, "WIL": wil}

# Function to convert audio to 16kHz and 16-bit
def convert_to_16kHz_16bit(input_path, output_path):
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_frame_rate(16000).set_sample_width(2)  # 2 bytes = 16 bits
    audio.export(output_path, format="wav")

# Process each .wav file and evaluate
results = []
for filename in sorted(os.listdir(audio_directory)):
    if filename.endswith(".wav"):
        file_path = os.path.join(audio_directory, filename)
        print(f"Processing {filename}...")

        sentence_id = "H" + re.search(r'\d+', filename).group().zfill(2)
        reference_text_list = ground_truth_dict.get(sentence_id)

        if not reference_text_list:
            print(f"Ground truth not found for {filename} with ID {sentence_id}")
            continue

        reference_text = " ".join(reference_text_list).replace(".", "")

        # Convert audio to 16kHz, 16-bit
        convert_to_16kHz_16bit(file_path, temp_audio_path)

        # Transcribe the audio using whisper.cpp with the specified model
        start_time = time.time()
        try:
            result = subprocess.run(
                [whisper_cpp_path, "-m", model_path, "-f", temp_audio_path, "-nt"],
                capture_output=True,
                text=True,
                check=True
            )
            hypothesis_text = result.stdout.strip()  # Captured transcription
        except subprocess.CalledProcessError as e:
            print(f"Error processing {filename}: {e}")
            continue
        end_time = time.time()
        
        elapsed_time = end_time - start_time
        
        # Evaluate transcription
        metrics = evaluate_transcription(reference_text, hypothesis_text)
        metrics.update({
            "Filename": filename,
            "Elapsed_Time": elapsed_time,
            "Hypothesis": hypothesis_text,
            "Reference": reference_text,
        })
        results.append(metrics)

        print(f"Processed {filename}:")
        print(f"  - Elapsed time: {elapsed_time:.2f}s")
        print(f"  - Hypothesis: {hypothesis_text}")
        print(f"  - Reference: {reference_text}")
        print(f"  - WER: {metrics['WER']:.2f}, MER: {metrics['MER']:.2f}, WIL: {metrics['WIL']:.2f}")

# Save results to a CSV file
results_df = pd.DataFrame(results)
results_df.to_csv("transcription_evaluation.csv", index=False)
