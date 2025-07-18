from pyannote.audio import Pipeline
import dotenv
import os
import sys
from pathlib import Path
import wave
import subprocess

# Add parent directory to Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from db import connect

# Connect to the database
conn = connect.connect_to_database()

# Load environment variables
dotenv.load_dotenv()
token = os.getenv("HUGGINGFACE_AUTH_TOKEN")

# Initialize the pipeline
pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token=token
)


# Path to the directory with .wav files
audio_directory = "/app/models/HARVARD_rawcopy"
results = []

# Process each audio file in the directory
for filename in sorted(os.listdir(audio_directory)):
    if filename.endswith(".wav"):
        file_path = os.path.join(audio_directory, filename)
        print(f"Processing {filename}...")

        # subprocess.run(["ffmpeg", "-i", file_path, "-ar", "16000", "-ac", "1", file_path])

        try:
            # Run the pipeline on the audio file
            
            diarization = pipeline(file_path)
            # Save diarization results to the database
            # Process diarization results
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                duration = turn.end - turn.start
                if duration >= 0.5:  # Ignore segments shorter than 0.5 seconds
                    print(f"start={turn.start:.1f}s stop={turn.end:.1f}s speaker_{speaker}")
                    connect.insert_diarization(conn, turn.start, turn.end, speaker, file_path)

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

# Close the database connection
if conn:
    conn.close()

