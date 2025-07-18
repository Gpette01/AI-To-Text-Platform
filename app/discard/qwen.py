import torchaudio
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
from pyAudioAnalysis import audioBasicIO, audioSegmentation as aS

# Load pre-trained model and processor for speech-to-text
stt_model_name = "facebook/wav2vec2-base-960h"
stt_model = Wav2Vec2ForCTC.from_pretrained(stt_model_name)
stt_processor = Wav2Vec2Processor.from_pretrained(stt_model_name)

# Load your audio file (replace 'your_audio.wav' with your audio file path)
audio_path = './file.wav'

try:
    waveform, sample_rate = torchaudio.load(audio_path)
    print(f"Sample rate: {sample_rate}")
except Exception as e:
    raise ValueError(f"Error loading audio file: {e}")

# Resample if necessary
if sample_rate != 16000:
    waveform = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)(waveform)

# Perform speaker diarization (simplified approach)
try:
    [Fs, x] = audioBasicIO.read_audio_file(audio_path)
except Exception as e:
    raise ValueError(f"Error reading audio file for diarization: {e}")

# Check if the audio data is not empty
if x.size == 0:
    raise ValueError("The audio file is empty or could not be read properly.")

segments = aS.speaker_diarization(x, Fs)  # Adjust this line according to the actual function signature

# Recognize speech
input_values = stt_processor(waveform.squeeze().numpy(), return_tensors="pt", sampling_rate=16000).input_values
with torch.no_grad():
    logits = stt_model(input_values).logits

# Get predicted ids
predicted_ids = torch.argmax(logits, dim=-1)

# Decode the ids to text
transcription = stt_processor.batch_decode(predicted_ids)[0]

print("Transcription:", transcription)
print("Speaker Diarization Segments:", segments)