import os
import time
from faster_whisper import WhisperModel
import jiwer
import re

# Initialize the model
model_size = "distil-large-v3"
model = WhisperModel(model_size, device="cpu", compute_type="int8")

# Path to the directory with .wav files
audio_directory = "HARVARD_raw"

# Load and process ground truth sentences
ground_truth_dict = {}
with open("harvsents.txt", "r") as f:
    current_group = None
    for line in f:
        group_match = re.match(r"H(\d+)", line)
        sentence_match = re.match(r"\s*(\d+)\.\s+(.*)", line)

        # If line has a group like "H1 Harvard Sentences", capture the group number
        if group_match:
            current_group = group_match.group(1).zfill(2)
            # print(f"Detected group: H{current_group}")  # Diagnostic print to confirm group detection
        # If line has a sentence like "1. The birch canoe slid on the smooth planks."
        elif sentence_match and current_group:
            # sentence_number = sentence_match.group(1).zfill(2)
            sentence_text = sentence_match.group(2).strip()
            # Construct key in format H01, H02, etc.
            key = f"H{current_group}"
            
            # Append the sentence_text to the dictionary
            if key in ground_truth_dict:
                ground_truth_dict[key].append(sentence_text)
            else:
                ground_truth_dict[key] = ["Harvard list number " + str(int(current_group))]
                ground_truth_dict[key].append(sentence_text)
                        
            # print(ground_truth_dict)
            
            # print(f"Added to dictionary: {key} -> {sentence_text}")  # Diagnostic print to confirm entry addition

# Function to get evaluation metrics
def evaluate_transcription(reference, hypothesis):
    wer = jiwer.wer(reference, hypothesis)
    mer = jiwer.mer(reference, hypothesis)
    wil = jiwer.wil(reference, hypothesis)
    return {"WER": wer, "MER": mer, "WIL": wil}

# Process each .wav file and evaluate
results = []
for filename in sorted(os.listdir(audio_directory)):
    if filename.endswith(".wav"):
        file_path = os.path.join(audio_directory, filename)
        print(f"Processing {filename}...")

        # Extract just the number from the filename to format as HXX
        sentence_id = "H" + re.search(r'\d+', filename).group().zfill(2)
        reference_text_list = ground_truth_dict.get(sentence_id)

        if not reference_text_list:
            print(f"Ground truth not found for {filename} with ID {sentence_id}")
            continue

        # Join the reference_text list into a single string
        reference_text = " ".join(reference_text_list).replace(".", "")
        
        # Transcribe the audio
        start_time = time.time()
        segments, _ = model.transcribe(file_path, beam_size=5)
        end_time = time.time()

        # Join transcriptions and calculate time
        hypothesis_text = " ".join([segment.text for segment in segments])
        elapsed_time = end_time - start_time
        # print(hypothesis_text)
        # print(reference_text)
        # Evaluate transcription
        metrics = evaluate_transcription(reference_text, hypothesis_text)
        metrics["Filename"] = filename
        metrics["Elapsed_Time"] = elapsed_time
        metrics["Hypothesis"] = hypothesis_text
        metrics["Reference"] = reference_text
        results.append(metrics)

        print(f"Processed {filename}:")
        print(f"  - Elapsed time: {elapsed_time:.2f}s")
        print(f"  - Hypothesis: {hypothesis_text}")
        print(f"  - Reference: {reference_text}")
        print(f"  - WER: {metrics['WER']:.2f}, MER: {metrics['MER']:.2f}, WIL: {metrics['WIL']:.2f}")

# Optional: Save results to a file
import pandas as pd
results_df = pd.DataFrame(results)
results_df.to_csv("transcription_evaluation.csv", index=False)
