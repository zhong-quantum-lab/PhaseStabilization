import os
import glob
import subprocess
import soundfile as sf
import json
import time
import requests
class RP_Streamer():
    def __init__(self, rp_ip, data_format="wav", port=8900, mode="raw", save_directory="./Dump"):
        self.red_pitaya_ip = rp_ip # Replace with your Red Pitaya's IP
        self.port = port# Port for streaming
        self.data_format = data_format # Format of the data (WAV file)
        self.mode = mode  # Data mode: 'raw' or 'volt'
        self.save_directory = save_directory  # Directory where WAV files are stored
        self.rpsa_client_path = "rpsa_client-2.00-35-aff683518/rpsa_client"
        # Clear storage directory
        files = glob.glob(os.path.join(self.save_directory, "*.*"))
        for file in files:
            os.remove(file)

    def capture_signal(self, samples):
        try:
            with subprocess.Popen(
                [
                    self.rpsa_client_path,
                    "--streaming",
                    f"--hosts={self.red_pitaya_ip}",
                    f"--port={self.port}",
                    f"--format={self.data_format}",
                    f"--limit={samples}",
                    f"--mode={self.mode}",
                    "--dir=" + self.save_directory,
                    "--verbose",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            ) as proc:
                #print(f"Capturing {samples} samples to WAV file in {self.save_directory}...")
                stdout, stderr = proc.communicate()  # Wait for the command to complete
                #print(stdout)
            return self.get_last_capture_data()

        except Exception as e:
            print(f"Error during data capture or processing: {e}")

    def get_last_capture_data(self):
        new_wav_files = glob.glob(os.path.join(self.save_directory, "*.wav"))
        if not new_wav_files:
            print("No file found after capture.")
        new_wav_file = max(new_wav_files, key=os.path.getctime)  # Get the newest file
        #print(f"Reading data from {new_wav_file}...")
        self.last_capture_data, self.last_capture_samplerate = sf.read(new_wav_file)  # Reads float32 data
        return self.last_capture_data, self.last_capture_samplerate

    def set_decimation(self, decimation):
        print(f"Sample rate = {125e3/decimation} (kHz)")
        config = {
            "adc_streaming": {
                "attenuator": 0,
                "calibration": True,
                "channels": 3,
                "coupling": 15,
                "decimation": decimation,  # Modify the decimation value
                "format": 0,
                "port": "8900",
                "protocol": 0,
                "resolution": 1,
                "samples": 20000000,
                "save_type": 0,
                "type": 1
            },
            "dac_streaming": {
                "dac_file": "",
                "dac_file_type": 0,
                "dac_gain": 0,
                "dac_memoryUsage": 1048576,
                "dac_mode": 0,
                "dac_port": "8903",
                "dac_repeat": -1,
                "dac_repeatCount": 1,
                "dac_speed": 125000000
            },
            "loopback": {
                "channels": 1,
                "dac_speed": -1,
                "mode": 0,
                "timeout": 1
            }
        }

        temp_config_file = "/tmp/streaming_config.json"
        with open(temp_config_file, "w") as f:
            json.dump(config, f, indent=4)

        remote_path = f"root@{self.red_pitaya_ip}:/root/.config/redpitaya/apps/streaming/streaming_config.json"
        scp_command = ["scp", temp_config_file, remote_path]

        try:
            print(f"Transferring updated config to {self.red_pitaya_ip}...")
            subprocess.run(scp_command, check=True)
            print("Decimation value updated and config file transferred successfully.")

        except subprocess.CalledProcessError as e:
            print(f"Error transferring config file: {e}")
