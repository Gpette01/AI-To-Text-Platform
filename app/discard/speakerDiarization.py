import sys
from transformers import AutoModel
import torchaudio
from pyannote.audio import Pipeline
from dotenv import load_dotenv
import os

def main(audio_file):
    # instantiate the pipeline
    # Load environment variables from .env file
    load_dotenv()

    # Get the authentication token from environment variables
    auth_token = os.getenv("HUGGINGFACE_AUTH_TOKEN")

    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token=auth_token
    )

    # run the pipeline on the provided audio file
    diarization = pipeline(audio_file, num_speakers=2)

    # dump the diarization output to disk using RTTM format
    output_file = audio_file.replace(".wav", ".rttm")
    with open(output_file, "w") as rttm:
        diarization.write_rttm(rttm)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python speakerDiarization.py <audio_file>")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    main(audio_file)
