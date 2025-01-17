import paramiko
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
matplotlib.use('TkAgg')  # Use the TkAgg backend for interactive plotting
import os
import fnmatch

def fetch_files_from_directory(host, username, password, remote_directory, files=[]):
    """
    Fetch specific files from a remote directory on Red Pitaya via SCP.

    Parameters:
    - host (str): IP or hostname of the Red Pitaya.
    - username (str): SSH username.
    - password (str): SSH password.
    - remote_directory (str): Remote directory to fetch files from.
    - files (list of str): List of filenames or wildcard patterns (e.g., "*.png").
    """
    try:
        # Set up SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, password=password)

        # Use SFTP to fetch the files
        with ssh.open_sftp() as sftp:
            # Ensure the local directory exists
            local_directory = os.path.basename(remote_directory) or "downloads"
            os.makedirs(local_directory, exist_ok=True)

            # List all files in the remote directory
            remote_files = sftp.listdir(remote_directory)

            # Filter files based on the provided list (supports wildcards)
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

# Plot the CSV data
def plot_csv_data(file_path):
    """Plot the data from the CSV file."""
    try:
        # Load the data
        data = np.loadtxt(file_path, delimiter=",")

        # Plot
        plt.figure(figsize=(10, 6))
        #time_points = [(i/16384) * 134.218 for i in range(len(data))]
        #plt.plot(time_points,data, label="Signal")
        plt.plot(data, label="Signal")
        plt.title("Signal Data from Red Pitaya")
        plt.xlabel("Time (ms)")
        plt.ylabel("Amplitude")
        plt.legend()
        plt.grid()

        # Compute the FFT
        fft_data = np.fft.fft(data)
        fft_freqs = np.fft.fftfreq(len(data), d=1/(2048*10**6))

        # Only consider the positive frequencies
        positive_freqs = fft_freqs[:len(data) // 2]
        positive_fft = np.abs(fft_data[:len(data) // 2])

        # Plot the FFT
        plt.figure(figsize=(10, 6))
        plt.plot(positive_freqs/(10**3), positive_fft, label="FFT", color="orange", linewidth=1.5)
        plt.title("FFT of Signal Data", fontsize=16)
        plt.xlabel("Frequency (kHz)", fontsize=14)
        plt.ylabel("Amplitude", fontsize=14)
        plt.legend(fontsize=12)
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.tight_layout()

        plt.show()
    except Exception as e:
        print(f"Error reading or plotting data: {e}")


# Main function
def main():
    # Connection details
    fetch_files_from_directory(
        host="205.208.56.215",
        username="root",
        password="root",
        remote_directory="/root",
        files=["data.csv", "*.png", "acquisition_data.csv"]
    )


    # Plot the data
    plot_csv_data("root/acquisition_data.csv")


if __name__ == "__main__":
    main()
