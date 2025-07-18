from rtlsdr import RtlSdr
import numpy as np

# Replace with your walkie-talkie's known frequency in Hz
known_freq = 446.03125e6 # Example frequency, channel 3

# Initialize SDR
sdr = RtlSdr()

try:
    # Configure SDR receiver parameters
    sdr.sample_rate = 2.4e6  # Sampling rate in Hz
    sdr.center_freq = known_freq  # Set the center frequency to the known frequency
    sdr.gain = 'auto'  # Automatic gain control
    sdr.freq_correction = 27 # PPM correction
    # sdr.freq_correction= 0.5

    # Read samples from the SDR
    samples = sdr.read_samples(2*1024*1024)

    # Perform FFT to find the frequency components
    fft_samples = np.fft.fftshift(np.fft.fft(samples))
    power = np.abs(fft_samples)

    # Generate frequency axis
    freq_axis = np.linspace(sdr.center_freq - sdr.sample_rate/2,
                            sdr.center_freq + sdr.sample_rate/2,
                            len(fft_samples))

    # Find the frequency with the maximum power
    peak_idx = np.argmax(power)
    measured_frequency = freq_axis[peak_idx]
    freq_diff_hz = known_freq - measured_frequency
    if abs(freq_diff_hz) < 1e3:
        print(f"Frequency difference: {freq_diff_hz} Hz")
    elif abs(freq_diff_hz) < 1e6:
        print(f"Frequency difference: {freq_diff_hz / 1e3} kHz")
    else:
        print(f"Frequency difference: {freq_diff_hz / 1e6} MHz")
    ppm_correction = ((known_freq - measured_frequency) / known_freq) * 1e6


    print(f"Measured frequency: {measured_frequency} Hz")
    print(f"Recommended PPM correction: {ppm_correction} ppm")

finally:
    # Close the SDR device
    sdr.close()
    import matplotlib.pyplot as plt

    # Convert frequency axis to MHz
    freq_axis_mhz = freq_axis / 1e6
    known_freq_mhz = known_freq / 1e6
    measured_frequency_mhz = measured_frequency / 1e6

    # Plot the FFT power spectrum
    # plt.figure(figsize=(10, 4))
    # plt.plot(freq_axis_mhz, 20 * np.log10(power))
    # plt.title('FFT Power Spectrum')
    # plt.xlabel('Frequency (MHz)')
    # plt.ylabel('Power (dB)')
    # plt.tight_layout()
    # plt.show()

    # Create a GridSpec layout with two columns
    fig = plt.figure(figsize=(12, 4))
    gs = fig.add_gridspec(1, 2, width_ratios=[3, 1])  # Wider plot area, narrow text area

    # Plot area
    ax = fig.add_subplot(gs[0])
    ax.axvline(x=known_freq_mhz, color='g', linestyle='--', label='Known Frequency')
    ax.axvline(x=measured_frequency_mhz, color='r', linestyle='--', label='Measured Frequency')
    ax.plot(freq_axis_mhz, 20 * np.log10(power))
    ax.set_title('Calibration Result')
    ax.set_xlabel('Frequency (MHz)')
    ax.set_ylabel('Power (dB)')
    ax.legend()
    ax.grid()

    # Text area on the right
    text_ax = fig.add_subplot(gs[1])
    text_ax.axis('off')  # Hide the axes for the text area

    # Display text information
    text_ax.text(0, 0.8, f'Frequency Difference: {freq_diff_hz / 1e3:.2f} kHz', color='black', fontsize=10)
    text_ax.text(0, 0.6, f'Known Frequency: {known_freq_mhz:.2f} MHz', color='green', fontsize=10)
    text_ax.text(0, 0.4, f'Measured Frequency: {measured_frequency_mhz:.2f} MHz', color='red', fontsize=10)

    plt.tight_layout()
    plt.show()
