import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import welch

# Load the data
def load_signal(filename):
    data = pd.read_csv(filename)
    time = data.iloc[:, 0].values  # First column is time
    signal = data.iloc[:, 1].values  # Second column is sample (voltage)
    return time, signal

# Compute the sampling rate
def compute_sampling_rate(time):
    dt = np.diff(time)  # Time differences
    return 1 / np.median(dt)  # Median sampling frequency

# Compute and plot the signals and PSDs
def plot_signals_and_psds(no_stable_file, stable_file):
    time_ns, signal_ns = load_signal(no_stable_file)
    time_s, signal_s = load_signal(stable_file)

    fs_ns = compute_sampling_rate(time_ns)
    fs_s = compute_sampling_rate(time_s)

    f_ns, Pxx_ns = welch(signal_ns, fs=fs_ns, nperseg=1024)
    f_s, Pxx_s = welch(signal_s, fs=fs_s, nperseg=1024)
    #f_ns, Pxx_ns = np.fft.fft(signal_ns, fs=fs_ns, nperseg=1024)
    #f_ns = fft_freqs = np.fft.fftfreq(len(signal_ns), d=1024)

    #f_s, Pxx_s = np.fft.fft(signal_s, fs=fs_s, nperseg=1024)

    psd_ratio = (Pxx_s/np.mean(Pxx_s)) / (Pxx_ns/np.mean(Pxx_ns))

    plt.figure(figsize=(10, 4))
    plt.plot(time_ns, signal_ns, label="Unstabilized", color='red', alpha=0.7)
    plt.xlabel("Time (s)")
    plt.ylabel("Voltage (V)")
    plt.title("Time Series: Unstabilized Signal")
    plt.legend()
    plt.grid(True)

    plt.figure(figsize=(10, 4))
    plt.plot(time_s, signal_s, label="Stabilized", color='blue', alpha=0.7)
    plt.xlabel("Time (s)")
    plt.ylabel("Voltage (V)")
    plt.title("Time Series: Stabilized Signal")
    plt.legend()
    plt.grid(True)

    plt.figure(figsize=(10, 6))
    plt.loglog(f_ns, Pxx_ns/np.mean(Pxx_ns), label="Unstabilized", linewidth=2, alpha=0.7, color='red')
    plt.loglog(f_s, Pxx_s/np.mean(Pxx_s), label="Stabilized", linewidth=2, alpha=0.7, color='blue')

    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Power Spectral Density (V²/Hz)")
    plt.title("Power Spectral Density Comparison: Stabilized vs. Unstabilized")
    plt.legend()
    plt.grid(True, which="both", linestyle="--", alpha=0.5)

    plt.figure(figsize=(10, 4))
    plt.semilogx(f_ns, psd_ratio, label="PSD Ratio (Stabilized / Unstabilized)", color='black', linewidth=2)
    plt.axhline(1, color='gray', linestyle="--", alpha=0.7)  # Reference line at 1
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("PSD Ratio")
    plt.title("Ratio of Stabilized to Unstabilized PSD")
    plt.legend()
    plt.grid(True, which="both", linestyle="--", alpha=0.5)

    plt.show()

plot_signals_and_psds("SavedData/NoStable.csv", "SavedData/Stable.csv")
