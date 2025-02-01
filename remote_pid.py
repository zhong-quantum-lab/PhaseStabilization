import subprocess

class RP_Pid:
    def __init__(self, ip):
        self.ip = ip
        self.pid_executable = "/root/PhaseStabilization/RedPitayaPid/pid"
        self.clear_executable = "/root/PhaseStabilization/RedPitayaPid/clear_pid"

    def set_pid(self, p, i, d):
        cmd = f"ssh root@{self.ip} '{self.pid_executable} {p} {i} {d}'"
        try:
            subprocess.run(cmd, shell=True, check=True)
            print(f"PID set: P={p}, I={i}, D={d}")
        except subprocess.CalledProcessError as e:
            print(f"Error setting PID: {e}")

    def clear_pid(self):
        cmd = f"ssh root@{self.ip} '{self.clear_executable}'"
        try:
            subprocess.run(cmd, shell=True, check=True)
            print("PID cleared.")
        except subprocess.CalledProcessError as e:
            print(f"Error clearing PID: {e}")
