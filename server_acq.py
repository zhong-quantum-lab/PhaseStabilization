import os
import glob
import subprocess
import soundfile as sf
import matplotlib.pyplot as plt

# Configuration
red_pitaya_ip = "205.208.56.215"  # Replace with your Red Pitaya's IP
port = 8900  # Port for streaming
data_format = "wav"  # Format of the data (WAV file)
sample_limit = 2000000  # Number of samples to capture
#sample_limit = 200  # Number of samples to capture
mode = "volt"  # Data mode: 'raw' or 'volt'
rpsa_client_path = "/home/halowens/Downloads/rpsa_client-2.00-35-aff683518/rpsa_client"
output_directory = "./Dump"  # Directory where WAV files are stored

# Step 1: Delete existing WAV files
files = glob.glob(os.path.join(output_directory, "*.*"))
for file in files:
    os.remove(file)

# Step 2: Run rpsa_client and wait for data capture
try:
    with subprocess.Popen(
        [
            rpsa_client_path,
            "--streaming",
            f"--hosts={red_pitaya_ip}",
            f"--port={port}",
            f"--format={data_format}",
            f"--limit={sample_limit}",
            f"--mode={mode}",
            "--dir=" + output_directory,
            "--verbose",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ) as proc:
        print(f"Capturing {sample_limit} samples to WAV file in {output_directory}...")
        stdout, stderr = proc.communicate()  # Wait for the command to complete
        print(stdout)
        print(stderr)

    # Step 3: Find the newly created WAV file
    new_wav_files = glob.glob(os.path.join(output_directory, "*.wav"))
    if not new_wav_files:
        print("No WAV file found after capture.")
        exit(1)
    new_wav_file = max(new_wav_files, key=os.path.getctime)  # Get the newest file

    # Step 4: Read and plot the WAV file using soundfile
    print(f"Reading data from {new_wav_file}...")
    data, samplerate = sf.read(new_wav_file)  # Reads float32 data
    print(f"Sample Rate: {samplerate}, Samples: {len(data)}")

    plt.figure(figsize=(10, 6))
    time = [(i+1)/samplerate for i in range(len(data))]
    plt.plot(time, data)
    plt.title(f"Captured Signal from Red Pitaya ({sample_limit} samples)")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude (Volts)")
    plt.grid(True)
    plt.show()

except Exception as e:
    print(f"Error during data capture or processing: {e}")
