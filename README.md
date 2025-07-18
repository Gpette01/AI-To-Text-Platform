# AI-Driven SDR Platform for Real-Time RF Signals to Text Transcription

## Overview

This project presents an innovative AI-driven Software Defined Radio (SDR) platform that captures radio frequency (RF) signals, processes them in real-time, and converts speech to text while providing advanced speaker identification and localization capabilities. The system is specifically designed for monitoring walkie-talkie communications in the 446 MHz band.

## 🚀 Key Features

### 📡 Software Defined Radio Processing
- **RTL-SDR Integration**: Real-time signal capture using RTL-SDR dongles
- **GNU Radio Framework**: Advanced signal processing, filtering, and demodulation
- **Automatic Channel Detection**: Intelligent frequency scanning and channel selection
- **Noise Filtering**: Sophisticated threshold-based noise reduction

### 🤖 AI-Powered Speech Processing
- **Model Support**: Integration of state-of-the-art ASR models:
  - Faster-Whisper (distil-large-v3)
- **Real-Time Transcription**: Continuous audio stream processing with timestamped output
- **Model Evaluation Framework**: Comprehensive benchmarking using Harvard sentences dataset

### 🎯 Speaker Intelligence
- **Direction of Arrival (DOA) Analysis**: Real-time speaker localization
- **DBSCAN Clustering**: Advanced clustering algorithm for speaker separation
- **Speaker Diarization**: Automatic speaker identification and tracking
- **Geolocation**: Transmitter location estimation using triangulation algorithms

### 🗄️ Data Management
- **SQLite Database**: Persistent storage for transcriptions, speaker data, and DOA measurements
- **Real-Time Data Processing**: Streaming data pipeline with threaded architecture
- **Historical Analysis**: Comprehensive logging and retrieval capabilities

### 🎨 Interactive Visualization
- **Real-Time Maps**: Live DOA visualization on interactive maps
- **Polar Plots**: Circular visualization of direction-finding data
- **GUI Interface**: Modern dark-themed interface using CustomTkinter
- **Multi-threaded Display**: Concurrent visualization and processing

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   RTL-SDR       │    │   GNU Radio      │    │   Audio         │
│   Hardware      │───▶│   Signal         │──▶│   Processing    │
│                 │    │   Processing     │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Real-Time     │    │   AI Speech      │    │   Speaker       │
│   Visualization │◀───│   Recognition    │◀──│   Diarization  │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
        │                       │                       │
        │              ┌──────────────────┐             │
        └─────────────▶│   SQLite         │◀───────────┘
                       │   Database       │
                       └──────────────────┘
```

## 📁 Project Structure

```
├── app/
│   ├── main.py                    # Main GUI application
│   ├── speechToTextLocal.py       # Real-time speech transcription
│   ├── clustering.py              # Speaker identification & clustering
│   ├── Localization.py           # Geolocation algorithms
│   ├── gnuradio/                 # SDR signal processing
│   │   ├── Thesis.py             # Main GNU Radio flowgraph
│   │   ├── findChannel.py        # Automatic channel detection
│   │   ├── calibrateRTL.py       # RTL-SDR calibration
│   │   └── runGNU.py             # GNU Radio controller
│   ├── models/                   # AI model evaluation
│   │   ├── evaluateWhisper.py    # Whisper model benchmarking
│   │   ├── evaluateFasterWhisper.py
│   │   ├── evaluateWav2Vec.py    # Wav2Vec2 evaluation
│   │   └── diarization.py        # Speaker diarization pipeline
│   ├── db/                       # Database management
│   │   ├── connect.py            # Database operations
│   │   └── initDB.py             # Database initialization
│   ├── kraken/                   # DOA simulation
│   └── discard/                  # Experimental components
├── docker-compose.yml            # Container orchestration
├── Dockerfile.dataset            # Docker environment
├── requirements.txt              # Python dependencies
└── entrypoint.sh                # Container startup script
```

## 🛠️ Installation & Setup

### Prerequisites
- Docker and Docker Compose
- RTL-SDR hardware
- Linux environment (Ubuntu recommended)
- HuggingFace account (for speaker diarization models)

### Hardware Requirements
- RTL-SDR dongle (compatible with RTL2832U)
- USB port for SDR connection
- Audio capabilities for output monitoring

### Software Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd Thesis-DOA_Clustering
```

2. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration:
# - HUGGINGFACE_AUTH_TOKEN
# - DOA_UDP_IP and DOA_UDP_PORT
# - CURRENT_LAT and CURRENT_LONG (for geolocation)
# - SILENCE_THRESHOLD (for audio processing)
```

3. **Build and run with Docker:**
```bash
docker-compose up --build
```

4. **Run the application inside the Docker container:**
```bash
docker exec -it dataset /bin/bash
cd app
python3 ./main.py
```

### Manual Installation

1. **Install system dependencies:**
```bash
sudo apt-get update
sudo apt-get install -y hackrf git cmake alsa-utils libuhd-dev \
    libhackrf-dev libgtk-3-dev ffmpeg xterm rtl-sdr gr-osmosdr \
    fonts-symbola
```

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Install Whisper.cpp (optional):**
```bash
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp
sh ./models/download-ggml-model.sh large-v3-turbo
make -j12
```

## 🚦 Usage

### Basic Operation

1. **Start the main application:**
```bash
python app/main.py
```

2. **The GUI provides several functions:**
   - **Start Transcription**: Begin real-time speech-to-text processing
   - **DOA Monitoring**: Visualize direction-of-arrival data on maps
   - **Channel Selection**: Automatic or manual frequency selection
   - **Model Selection**: Choose between different AI models

### Advanced Configuration

#### RTL-SDR Setup
```python
# Configure in app/gnuradio/findChannel.py
frequencies = [446.00625e6, 446.01875e6, 446.03125e6, ...]  # Target frequencies
sample_rate = 2.048e6  # Sample rate
gain = 'auto'  # Gain setting
```

#### AI Model Configuration
```python
# In app/speechToTextLocal.py
model_size = "distil-large-v3"  # Whisper model variant
device = "cpu"  # or "cuda" for GPU acceleration
compute_type = "int8"  # Quantization level
```

### API Integration

The system exposes several interfaces:

#### UDP DOA Data
```python
# DOA data format (JSON)
{
    "timestamp": "2024-01-01T12:00:00",
    "theta_0": 180.5  # Direction in degrees
}
```

#### Database Queries
```python
# Retrieve transcriptions
transcriptions = retreive_text(conn, wavFile)

# Insert DOA measurement
insert_doa(conn, timestamp, doa_angle)
```

## 🧪 Model Evaluation

### Evaluation Datasets
- Harvard Sentences: Standard phonetically balanced sentences
- Custom walkie-talkie recordings
- Noise-corrupted speech samples


## 🗺️ Direction of Arrival & Localization

### DOA Processing
- **Real-time Analysis**: Continuous DOA measurements from KrakenSDR or simulated data
- **Clustering**: DBSCAN algorithm for speaker separation
- **Visualization**: Polar plots and map overlays

### Localization Algorithms
```python
# Example usage
transmitter_lat, transmitter_lon, residuals = localize_transmitter(
    receiver_lat=35.1456591,
    receiver_lon=33.4152348,
    doa_degs=[181, 179, 174, 186, 189]
)
```

## 🔧 Configuration

### Environment Variables
```bash
# Audio processing
SILENCE_THRESHOLD=0.1

# Geolocation
CURRENT_LAT=35.1456591
CURRENT_LONG=33.4152348

# DOA Communication
DOA_UDP_IP=127.0.0.1
DOA_UDP_PORT=4200

# AI Models
HUGGINGFACE_AUTH_TOKEN=your_token_here
```

### GNU Radio Parameters
```python
# Signal processing parameters
samp_rate = 2.4e6        # Sample rate
gain = 40                # RF gain
bw = 12500              # Bandwidth
fc = 446.03125e6        # Center frequency
```

## 🐛 Troubleshooting

### Common Issues

1. **RTL-SDR Not Detected**
```bash
# Check device connection
rtl_test -t 1

# Verify permissions
sudo usermod -a -G plugdev $USER
```

2. **Audio Issues**
```bash
# Check audio devices
aplay -l

# Test audio output
speaker-test -c2
```

3. **Model Loading Errors**
```bash
# Check disk space for models
df -h

# Verify internet connection for downloads
ping huggingface.co
```

### Performance Optimization

1. **GPU Acceleration**
```python
# Enable CUDA for supported models
device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
```

2. **Memory Management**
```python
# Optimize for low-memory systems
compute_type = "int8"  # Use quantized models
```

## 📚 Technical References

### Signal Processing
- GNU Radio framework documentation
- RTL-SDR hardware specifications
- Digital signal processing principles

### AI/ML Models
- [Faster-Whisper](https://github.com/guillaumekln/faster-whisper)

### Direction Finding
- DBSCAN clustering algorithm
- Triangulation methods for RF localization
- Direction of arrival estimation techniques


## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- GNU Radio community for the excellent SDR framework
- OpenAI for the Whisper speech recognition models
- RTL-SDR project for affordable SDR hardware
- HuggingFace for hosting and distributing AI models
- PyQt/Tkinter communities for GUI frameworks

---

**Note**: This project is designed for educational and research purposes. Ensure compliance with local regulations regarding radio frequency monitoring and privacy laws. 
