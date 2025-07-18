import torch
import torchaudio
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import socket
import numpy as np

def samples_to_numpy(samples, sample_rate=16000):
    samples = np.frombuffer(samples, dtype=np.int16)
    samples = samples.astype(np.float32) / np.iinfo(np.int16).max
    return samples

def chunk_audio(samples, chunk_duration=30, sample_rate=16000):
    chunk_size = int(chunk_duration * sample_rate)
    return [samples[i:i+chunk_size] for i in range(0, len(samples), chunk_size)]

def transcribe_audio(asr_pipeline, samples, sample_rate=16000, chunk_duration=30):
    generate_kwargs = {
        "task": "transcribe",
        "language": "en",
    }
    
    if len(samples) > chunk_duration * sample_rate:
        # Long audio: use chunking
        chunks = chunk_audio(samples, chunk_duration, sample_rate)
        transcriptions = []
        for i, chunk in enumerate(chunks):
            result = asr_pipeline(chunk, return_timestamps=True, generate_kwargs=generate_kwargs)
            transcriptions.append(f"Chunk {i+1}: {result['text']}")
        return "\n".join(transcriptions)
    else:
        # Short audio: transcribe directly
        result = asr_pipeline(samples, generate_kwargs=generate_kwargs)
        return result["text"]

def defineModel():
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    
    model_id = "openai/whisper-large-v3-turbo"
    
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
    )
    model.to(device)
    
    processor = AutoProcessor.from_pretrained(model_id)
    
    return pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        torch_dtype=torch_dtype,
        device=device,
    )

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 5555)
    print(f'Starting server on {server_address[0]}:{server_address[1]}')
    server_socket.bind(server_address)
    server_socket.listen(5)
    
    asr_pipeline = defineModel()
    
    while True:
        print('Waiting for a connection...')
        client_socket, client_address = server_socket.accept()
        try:
            print(f'Connection from {client_address}')
            
            data = bytearray()
            while True:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                data.extend(chunk)
            
            if data:
                try:
                    samples = samples_to_numpy(data)
                    print(f"Samples shape: {samples.shape}, dtype: {samples.dtype}")
                    
                    result = transcribe_audio(asr_pipeline, samples)
                    
                    print("Transcription:")
                    print(result)
                    
                except Exception as e:
                    print(f"Error processing audio data: {e}")
                    print(f"Full error: {str(e)}")
        finally:
            client_socket.close()

if __name__ == '__main__':
    start_server()