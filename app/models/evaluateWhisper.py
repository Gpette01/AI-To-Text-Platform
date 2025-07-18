import os
import time
import torch
import re
import jiwer
import contextlib
import pandas as pd
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

# Setup device and model
device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

model_id = "openai/whisper-large-v3-turbo"
model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
).to(device)
processor = AutoProcessor.from_pretrained(model_id)

pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    torch_dtype=torch_dtype,
    device=device,
    return_timestamps=True,
)

# Path to the directory with .wav files
audio_directory = "HARVARD_raw"

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
        
        # Transcribe the audio
        start_time = time.time()
        with open(os.devnull, 'w') as fnull, contextlib.redirect_stderr(fnull):
            result = pipe(file_path)
        end_time = time.time()
        
        hypothesis_text = result["text"]
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
