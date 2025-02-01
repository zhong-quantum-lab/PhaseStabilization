import paramiko
import matplotlib.pyplot as plt
import numpy as np
import matplotlib

matplotlib.use('TkAgg')  # Use the TkAgg backend for interactive plotting
import os
import fnmatch


def fetch_files_from_directory(host, username, password, remote_directory, files=[]):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, password=password)

        with ssh.open_sftp() as sftp:
            local_directory = os.path.basename(remote_directory) or "downloads"
            os.makedirs(local_directory, exist_ok=True)

            remote_files = sftp.listdir(remote_directory)
            for pattern in files:
                matching_files = fnmatch.filter(remote_files, pattern)
                for file in matching_files:
                    remote_file_path = os.path.join(remote_directory, file)
                    local_file_path = os.path.join(local_directory, file)
                    sftp.get(remote_file_path, local_file_path)
                    print(f"File successfully copied: {remote_file_path} -> {local_file_path}")

    except Exception as e:
        print(f"Error fetching files: {e}")
    finally:
        ssh.close()


def plot_csv_data(signal, time_points, volts=True, fft=False):
    plt.figure(figsize=(10, 6))
    if volts:
        signal = signal / 8196
    plt.plot(time_points, signal, label="Signal")
    plt.title("Signal Data from Red Pitaya", fontsize=16)
    plt.xlabel("Time (s)", fontsize=14)
    plt.ylabel("Amplitude", fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()

    if fft:
        sampling_interval = time_points[1] - time_points[0]  # Calculate sampling interval from time data
        fft_data = np.fft.fft(signal)
        fft_freqs = np.fft.fftfreq(len(signal), d=sampling_interval)

        # Only consider the positive frequencies
        positive_freqs = fft_freqs[:len(signal) // 2]
        positive_fft = np.abs(fft_data[:len(signal) // 2])

        # Plot the FFT
        plt.figure(figsize=(10, 6))
        plt.plot(positive_freqs / 1e3, positive_fft, label="FFT", color="orange", linewidth=1.5)
        plt.title("FFT of Signal Data", fontsize=16)
        plt.xlabel("Frequency (kHz)", fontsize=14)
        plt.ylabel("Amplitude", fontsize=14)
        plt.legend(fontsize=12)
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.tight_layout()
    plt.show()


def analyze_locking_time(signal, time_points):
    def in_range(val):
        lock_value = 1756
        lock_width = 5
        return lock_value + lock_width > val > lock_value - lock_width

    only_locked = [in_range(val) for val in signal]
    filter_cutoff = 200
    time_width = time_points[1]
    in_sequence = False
    sequence_lengths = []
    seq_length = 0
    for locked in only_locked:
        if locked:
            if not in_sequence:
                in_sequence = True
                seq_length = 1
            else:
                seq_length += 1
        else:
            if in_sequence:
                in_sequence = False
                if seq_length > filter_cutoff:
                    sequence_lengths.append(seq_length)
    print(f"Number of locked sequences = {len(sequence_lengths)}")
    print(f"One sample is {time_width} long")
    print(f"Locking Length cutoff is {time_width * filter_cutoff}")
    print(f"Average Lock Time {np.mean(sequence_lengths) * time_width}")
    plt.figure()
    plt.plot(time_points, signal)
    plt.figure()
    plt.plot(only_locked)
    plt.show()
    return np.mean(sequence_lengths) * time_width

    pass


# Main function
def main():
    # Connection details
    fetch_files_from_directory(
        host="205.208.56.215",
        username="root",
        password="root",
        remote_directory="/root/PhaseStabilization/RedPitayaPid/",
        files=["data.csv", "*.png", "acquisition_data.csv"]
    )

    # Plot the data
    data = np.loadtxt("downloads/acquisition_data.csv", delimiter=",")
    # Extract time points and signal values
    time_points = data[:, 0]
    signal = data[:, 1]
    plot_csv_data(signal, time_points, volts=False)
    average_lock_time = analyze_locking_time(signal, time_points)


if __name__ == "__main__":
    main()
