import subprocess

class RP_Pid:
    def __init__(self, ip):
        self.ip = ip
        self.password = "root"
        self.pid_executable = "/root/PhaseStabilization/RedPitayaPid/pid"
        self.clear_executable = "/root/PhaseStabilization/RedPitayaPid/clear_pid"

    def set_pid(self, channel, p, i, d, set_point):
        cmd = f"sshpass -p '{self.password}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@{self.ip} '{self.pid_executable} {channel} {p} {i} {d} {set_point}'"
        try:
            subprocess.run(cmd, shell=True, check=True)
            print(f"PID set: Channel={channel}, P={p}, I={i}, D={d}, Setpoint={set_point}")
        except subprocess.CalledProcessError as e:
            print(f"Error setting PID: {e}")

    def clear_pid(self):
        cmd = f"sshpass -p '{self.password}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@{self.ip} '{self.clear_executable}'"
        try:
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error clearing PID: {e}")

