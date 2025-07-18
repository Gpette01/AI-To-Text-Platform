import numpy as np
from rtlsdr import RtlSdr
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from dotenv import load_dotenv
import os
import sys
# from ..clustering import setBand
# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from clustering import setBand

load_dotenv('/etc/profile.d/rtl_device_index.sh')
SAMPLES = float(os.getenv("FINDCHANNEL_SAMPLES", 4*1024))
MULTIPLIER = float(os.getenv("FINDCHANNEL_MULTIPLIEs", 10))
RTL_INDEX_DEVICE = int(os.getenv('RTL_DEVICE_INDEX'))


def scan_frequency(frequency, sdr):
    sdr.center_freq = frequency
    samples = sdr.read_samples(SAMPLES)

    return samples

def detect_signal(samples):
    # Perform FFT on the samples
    spectrum = np.fft.fftshift(np.fft.fft(samples))
    power = np.abs(spectrum)**2
    return power

def detect_peaks(power, multiplier=MULTIPLIER):
    threshold = multiplier * np.median(power)  # adaptive threshold based on median noise level
    peaks, properties = find_peaks(power, height=threshold)
    return peaks, properties

def plot_spectrum(power, frequency, peaks, sdr):
    freqs = np.fft.fftfreq(len(power), 1.0 / sdr.sample_rate)
    plt.figure(figsize=(10, 6))
    plt.plot(np.fft.fftshift(freqs) + frequency, power)
    plt.scatter(np.fft.fftshift(freqs)[peaks] + frequency, power[peaks], color='red')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Power')
    plt.title(f'Spectrum around {frequency/1e6} MHz')
    plt.show()

def findChannel():
    # Initialize a new SDR instance
    sdr = RtlSdr(device_index=RTL_INDEX_DEVICE)
    sdr.sample_rate = 2.048e6
    sdr.gain = 'auto'
    sdr.freq_correction = 23  # PPM correction
    
    # List of specific frequencies to scan
    frequencies = [446.00625e6, 446.01875e6, 446.03125e6, 446.04375e6, 446.05625e6, 446.06875e6, 446.08125e6, 446.09375e6]
    
    npArray = np.array(frequencies)
    
    freq = npArray.mean()

    # Scan the specific list of frequencies
    # freq += 3e3  # Offset to avoid DC spike
    # print(f"Scanning {freq/1e6} MHz")

    samples = scan_frequency(freq, sdr)
    power = detect_signal(samples)
    peaks, properties = detect_peaks(power)

    if peaks.size > 0:
        peak_amplitude = properties['peak_heights'].max()
        peak_frequency = freq + np.fft.fftshift(np.fft.fftfreq(len(power), 1.0 / sdr.sample_rate))[peaks][properties['peak_heights'].argmax()]
        # print(f"Max peak amplitude: {peak_amplitude} at frequency {peak_frequency/1e6} MHz")
    else:
        print("No significant peaks detected")
        return None
    #plot_spectrum(power, freq, peaks, sdr)

    # Close the SDR
    sdr.close()
    if not (frequencies[0]-0.0125e6) <= peak_frequency <= (frequencies[len(frequencies)-1]+0.0125e6):
        print("Frequency not in range, default is 1st channel")
        setBand(frequencies[0]/1e6)
        return frequencies[0]/1e6
     
    if peak_amplitude > 0:
        print(f"Max peak amplitude: {10 * np.log10(peak_amplitude)} at frequency {peak_frequency/1e6} MHz")
        setBand(peak_frequency/1e6)
        closest_channel = min(frequencies, key=lambda x: abs(x - peak_frequency))
        print(f"Closest channel frequency: {closest_channel/1e6} MHz")
        print(f"Channel number: {frequencies.index(closest_channel) + 1}")
        return closest_channel/1e6
    else:
        print("No significant peaks detected")
        return None
    
import time
def collectData(dataPoints, distance):
    # Initialize a new SDR instance
    sdr = RtlSdr(device_index=RTL_INDEX_DEVICE)
    sdr.sample_rate = 2.048e6
    sdr.gain = 'auto'
    sdr.freq_correction = 23  # PPM correction
    
    # List of specific frequencies to scan
    frequencies = [446.00625e6, 446.01875e6, 446.03125e6, 446.04375e6, 446.05625e6, 446.06875e6, 446.08125e6, 446.09375e6]
    
    npArray = np.array(frequencies)
    
    freq = npArray.mean()

    # Scan the specific list of frequencies
    # freq += 3e3  # Offset to avoid DC spike
    # print(f"Scanning {freq/1e6} MHz")
    while True:
        samples = scan_frequency(freq, sdr)
        power = detect_signal(samples)
        peaks, properties = detect_peaks(power)

        if peaks.size > 0:
            peak_amplitude = properties['peak_heights'].max()
            peak_frequency = freq + np.fft.fftshift(np.fft.fftfreq(len(power), 1.0 / sdr.sample_rate))[peaks][properties['peak_heights'].argmax()]
            # print(f"Max peak amplitude: {peak_amplitude} at frequency {peak_frequency/1e6} MHz")
        else:
            print("No significant peaks detected")
            return None
    
        if not (frequencies[0]-0.0125e6) <= peak_frequency <= (frequencies[len(frequencies)-1]+0.0125e6):
            print("Frequency not in range, default is 1st channel")
            continue
        if peak_amplitude > 0:
            print(f"Max peak amplitude: {10 * np.log10(peak_amplitude)} at frequency {peak_frequency/1e6} MHz")
            closest_channel = min(frequencies, key=lambda x: abs(x - peak_frequency))
            with open("distance.txt", "a") as file:
                file.write(f"{peak_amplitude}, {10 * np.log10(peak_amplitude)}, {distance}, {frequencies.index(closest_channel) + 1}\n")
            print(f"Closest channel frequency: {closest_channel/1e6} MHz")
            print(f"Channel number: {frequencies.index(closest_channel) + 1}")
        else:
            print("No significant peaks detected")
        time.sleep(0.1)
    #plot_spectrum(power, freq, peaks, sdr)

    # Close the SDR
    
    sdr.close()
    # if not (frequencies[0]-0.0125e6) <= peak_frequency <= (frequencies[len(frequencies)-1]+0.0125e6):
    #     print("Frequency not in range, default is 1st channel")
    #     return frequencies[0]/1e6
     
    # if peak_amplitude > 0:
    #     print(f"Max peak amplitude: {10 * np.log10(peak_amplitude)} at frequency {peak_frequency/1e6} MHz")
    #     with open("distance.txt", "a") as file:
    #         file.write(f"{peak_amplitude}, {10 * np.log10(peak_amplitude)}, 10\n")
    #     closest_channel = min(frequencies, key=lambda x: abs(x - peak_frequency))
    #     print(f"Closest channel frequency: {closest_channel/1e6} MHz")
    #     print(f"Channel number: {frequencies.index(closest_channel) + 1}")
    #     return closest_channel/1e6
    # else:
    #     print("No significant peaks detected")
    #     return None

if __name__ == "__main__":
    # findChannel()
    collectData(10, 10000000000)
    # sdr.close()

