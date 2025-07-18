import noisereduce as nr
import librosa
import soundfile as sf

# Load walkie-talkie audio
audio, sr = librosa.load("HARVARD_rawcopy/Harvard_list_01.wav", sr=None)

# Apply noise reduction
reduced_noise = nr.reduce_noise(
    y=audio,                  # Input signal
    sr=sr,                    # Sample rate
    stationary=False,         # Non-stationary noise reduction
    prop_decrease=0.8,        # Proportion of noise reduction
    time_constant_s=1.0,      # Time constant for noise floor (in seconds)
    freq_mask_smooth_hz=300,  # Frequency smoothing
    time_mask_smooth_ms=40,   # Time smoothing
    thresh_n_mult_nonstationary=1.5, # Threshold multiplier for non-stationary
    sigmoid_slope_nonstationary=10, # Slope of sigmoid in non-stationary
    n_fft=1024,               # FFT window size
    win_length=800,           # Window length
    hop_length=400,           # Hop length for overlapping
    n_jobs=-1                 # Use all CPU cores
)

# Save the enhanced audio
sf.write("enhanced_audio.wav", reduced_noise, sr)