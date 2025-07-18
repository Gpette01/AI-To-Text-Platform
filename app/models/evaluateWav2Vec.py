import os
import time
import re
import jiwer
import pandas as pd
from pydub import AudioSegment
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import torch
import librosa

# Path to the directory with .wav files
audio_directory = "HARVARD_raw"
temp_audio_path = "temp_audio_16kHz_16bit.wav"  # Temporary file to hold 16kHz, 16-bit audio

# Load the Wav2Vec2 model and processor
wav2vec_model_id = "facebook/wav2vec2-large-960h"
wav2vec_model = Wav2Vec2ForCTC.from_pretrained(wav2vec_model_id).to("cuda" if torch.cuda.is_available() else "cpu")
wav2vec_processor = Wav2Vec2Processor.from_pretrained(wav2vec_model_id)

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

# Function to transcribe audio with Wav2Vec2
def transcribe_with_wav2vec2(audio_path):
    audio_input, _ = librosa.load(audio_path, sr=16000)
    input_values = wav2vec_processor(audio_input, return_tensors="pt", sampling_rate=16000).input_values
    input_values = input_values.to(wav2vec_model.device)
    with torch.no_grad():
        logits = wav2vec_model(input_values).logits
    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = wav2vec_processor.batch_decode(predicted_ids)[0]
    return transcription

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

        # Transcribe the audio using Wav2Vec2
        start_time = time.time()
        wav2vec_hypothesis = transcribe_with_wav2vec2(file_path).lower()
        elapsed_time = time.time() - start_time

        # Evaluate transcription
        metrics = evaluate_transcription(reference_text, wav2vec_hypothesis)
        metrics.update({
            "Model": "Wav2Vec2",
            "Filename": filename,
            "Elapsed_Time": elapsed_time,
            "Hypothesis": wav2vec_hypothesis,
            "Reference": reference_text,
        })
        results.append(metrics)

        print(f"Processed {filename} with Wav2Vec2:")
        print(f"  - Elapsed time: {elapsed_time:.2f}s")
        print(f"  - Hypothesis: {wav2vec_hypothesis}")
        print(f"  - Reference: {reference_text}")
        print(f"  - WER: {metrics['WER']:.2f}, MER: {metrics['MER']:.2f}, WIL: {metrics['WIL']:.2f}")

# Save results to a CSV file
results_df = pd.DataFrame(results)
results_df.to_csv("transcription_evaluation_wav2vec.csv", index=False)
