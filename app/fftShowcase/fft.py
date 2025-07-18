import numpy as np
import matplotlib.pyplot as plt

# Parameters
sampling_rate = 1000  # samples per second
duration = 1  # seconds
t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)

# Generate two sine wave signals
frequency1 = 5  # frequency of the first signal in Hz
frequency2 = 50  # frequency of the second signal in Hz
signal1 = np.sin(2 * np.pi * frequency1 * t)  # 5 Hz sine wave
signal2 = np.sin(2 * np.pi * frequency2 * t)  # 50 Hz sine wave

# Add the signals together
combined_signal = signal1 + signal2

# Perform FFT on the combined signal
fft_result = np.fft.fft(combined_signal)
fft_freqs = np.fft.fftfreq(len(combined_signal), 1 / sampling_rate)

# Calculate the magnitude of the FFT result
magnitude = np.abs(fft_result[:len(fft_result) // 2])
positive_freqs = fft_freqs[:len(fft_freqs) // 2]

# Identify the peaks
peak_indices = np.where(magnitude > 0.5 * np.max(magnitude))[0]
peak_frequencies = positive_freqs[peak_indices]
peak_magnitudes = magnitude[peak_indices]

# Perform inverse FFT to reconstruct the original time signal
reconstructed_signal = np.fft.ifft(fft_result).real

# Plot time domain signals
plt.figure(figsize=(12, 10))

# Plot original signals in time domain
plt.subplot(4, 1, 1)
plt.plot(t, signal1, label="5 Hz Signal")
plt.plot(t, signal2, label="50 Hz Signal")
plt.title("Original Signals in Time Domain")
plt.xlabel("Time [s]")
plt.ylabel("Amplitude")
plt.legend()

# Plot combined signal in time domain
plt.subplot(4, 1, 2)
plt.plot(t, combined_signal, label="Combined Signal (5 Hz + 50 Hz)", color="purple")
plt.title("Combined Signal in Time Domain")
plt.xlabel("Time [s]")
plt.ylabel("Amplitude")
plt.legend()

# Plot FFT result (magnitude spectrum)
plt.subplot(4, 1, 3)
plt.plot(positive_freqs, magnitude, label="FFT Magnitude Spectrum")
plt.title("FFT of Combined Signal")
plt.xlabel("Frequency [Hz]")
plt.ylabel("Magnitude")

# Highlight peaks and annotate values
for freq, mag in zip(peak_frequencies, peak_magnitudes):
    plt.plot(freq, mag, 'ro')  # Highlight peak with red dot
    plt.text(freq, mag, f"{freq:.1f} Hz\n{mag:.2f}", ha='center', va='bottom', fontsize=9)

plt.grid(True)

# Plot reconstructed signal in time domain
plt.subplot(4, 1, 4)
plt.plot(t, reconstructed_signal, label="Reconstructed Signal", color="green")
plt.title("Reconstructed Signal from Inverse FFT")
plt.xlabel("Time [s]")
plt.ylabel("Amplitude")
plt.legend()

plt.tight_layout()
plt.show()
