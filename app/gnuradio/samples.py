import numpy as np
from rtlsdr import RtlSdr
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import time

# Initialize the SDR
sdr = RtlSdr()

# Configure the SDR
sdr.sample_rate = 2.048e6  # 2.048 MHz
sdr.gain = 'auto'
sdr.freq_correction = 23  # PPM correction

def scan_frequency(frequency, sample_size):
    sdr.center_freq = frequency
    samples = sdr.read_samples(sample_size)
    return samples

def detect_signal(samples):
    # Perform FFT on the samples
    spectrum = np.fft.fftshift(np.fft.fft(samples))
    power = np.abs(spectrum)**2
    return power

def detect_peaks(power, threshold=1e6):
    peaks, properties = find_peaks(power, height=threshold)
    return peaks, properties

def plot_spectrum(power, frequency, sample_size, peaks):
    freqs = np.fft.fftfreq(len(power), 1.0 / sdr.sample_rate)
    power_dB = 10 * np.log10(power / np.max(power))
    plt.figure(figsize=(10, 6))
    plt.plot(np.fft.fftshift(freqs) + frequency, power_dB)
    plt.scatter(np.fft.fftshift(freqs)[peaks] + frequency, power_dB[peaks], color='red')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Power Spectral Density (dB)')
    plt.title(f'Spectrum around {frequency/1e6} MHz\nSample Size: {sample_size}')
    plt.show()

# Specific frequency to scan
frequency = 446.05e6  # Offset to avoid DC spike

# List of sample sizes to try
sample_sizes = [1024,2*1024,4*1024,8*1024,16*1024,32*1024, 64*1024, 128*1024, 256*1024, 512*1024, 1024*1024, 2*1024*1024, 4*1024*1024, 8*1024*1024, 16*1024*1024, 32*1024*1024]


for sample_size in sample_sizes:
    start_time = time.time()
    samples = scan_frequency(frequency, sample_size)
    power = detect_signal(samples)
    peaks, properties = detect_peaks(power)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"{sample_size}, {elapsed_time:.4f}")
    plot_spectrum(power, frequency, sample_size, peaks)

# Close the SDR
sdr.close()
