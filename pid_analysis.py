import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch
from remote_pid import RP_Pid
from remote_streaming import RP_Streamer

def plot_pid_comparison(data_unstable, data_stable, samplerate):
    time = np.arange(len(data_unstable)) / samplerate  # Compute time axis

    channel_1_unstable = data_unstable[:, 0]  # Interferometer signal (Unstabilized)
    channel_1_stable = data_stable[:, 0]  # Interferometer signal (Stabilized)

    if data_unstable.shape[1] == 2:
        channel_2_unstable = data_unstable[:, 1]  # PID channel (Unstabilized)
        channel_2_stable = data_stable[:, 1]  # PID channel (Stabilized)
    else:
        channel_2_unstable, channel_2_stable = None, None

    plt.figure(figsize=(10, 4))
    plt.plot(time, channel_1_unstable, label="Unstabilized", color='red', alpha=0.7)
    if channel_2_unstable is not None:
        plt.plot(time, channel_2_unstable, label="PID", linestyle="dotted", color="blue", alpha=0.5)
    plt.xlabel("Time (s)")
    plt.ylabel("Voltage (V)")
    plt.title("No PID Stabilization")
    plt.legend()
    plt.grid(True)

    plt.figure(figsize=(10, 4))
    plt.plot(time, channel_1_stable, label="Stabilized", color='red', alpha=0.7)
    if channel_2_stable is not None:
        plt.plot(time, channel_2_stable, label="PID", linestyle="dotted", color="blue", alpha=0.5)
    plt.xlabel("Time (s)")
    plt.ylabel("Voltage (V)")
    plt.title("PID Stabilization")
    plt.legend()
    plt.grid(True)

    f_unstable, Pxx_unstable = welch(channel_1_unstable, fs=samplerate, nperseg=1024)
    f_stable, Pxx_stable = welch(channel_1_stable, fs=samplerate, nperseg=1024)

    N = len(channel_1_unstable)
    f_unstable = np.fft.fftfreq(N, d=1 / samplerate)[:N // 2]
    Pxx_unstable = (np.abs(np.fft.fft(channel_1_unstable)) ** 2) / N
    Pxx_unstable = Pxx_unstable[:N // 2]  # Keep only positive frequencies
   # Pxx_unstable = Pxx_unstable / np.mean(Pxx_unstable)

    N = len(channel_1_stable)
    f_stable = np.fft.fftfreq(N, d=1 / samplerate)[:N // 2]
    Pxx_stable = (np.abs(np.fft.fft(channel_1_stable)) ** 2) / N
    Pxx_stable = Pxx_stable[:N // 2]  # Keep only positive frequencies
    #Pxx_stable = Pxx_stable / np.mean(Pxx_stable)

    plt.figure(figsize=(10, 6))
    plt.loglog(f_unstable, Pxx_unstable, label="Unstabilized", linewidth=2, alpha=0.7,
               color='red')
    plt.loglog(f_stable, Pxx_stable, label="Stabilized", linewidth=2, alpha=0.7, color='blue')
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Power Spectral Density (V²/Hz)")
    plt.title("Power Spectral Density Comparison: Stabilized vs. Unstabilized")
    plt.legend()
    plt.grid(True, which="both", linestyle="--", alpha=0.5)

    psd_ratio = (Pxx_stable / np.mean(Pxx_stable)) / (Pxx_unstable / np.mean(Pxx_unstable))

    plt.figure(figsize=(10, 4))
    plt.semilogx(f_unstable, psd_ratio, label="PSD Ratio (Stabilized / Unstabilized)", color='black', linewidth=2)
    plt.axhline(1, color='gray', linestyle="--", alpha=0.7)  # Reference line at 1
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("PSD Ratio")
    plt.title("Ratio of Stabilized to Unstabilized PSD")
    plt.legend()
    plt.grid(True, which="both", linestyle="--", alpha=0.5)

    plt.show()


pid_pitaya_ip = "205.208.56.215"
capture_pitaya_ip = "10.120.12.220"
captures = 1000000
streamer = RP_Streamer(capture_pitaya_ip)
pid = RP_Pid(pid_pitaya_ip)
#streamer.set_decimation(512)
pid.clear_pid()
data_unstable, samplerate = streamer.capture_signal(captures)
pid.set_pid(3500, 750, 0)
data_stable, _samplerate = streamer.capture_signal(captures)

plot_pid_comparison(data_unstable, data_stable, samplerate)
