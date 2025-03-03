import asyncio
import websockets

class RP_Pid:
    def __init__(self, ip):
        self.ws_url = f"ws://{ip}:8765"  # WebSocket server URL
        self.pid_executable = "/root/PhaseStabilization/RedPitayaPid/pid"
        self.clear_executable = "/root/PhaseStabilization/RedPitayaPid/clear_pid"

    async def send_command(self, command):
        try:
            async with websockets.connect(self.ws_url) as websocket:
                await websocket.send(command)  # Send the command
                response = await websocket.recv()  # Receive output
                return response
        except Exception as e:
            print(f"WebSocket Error: {e}")
            return None

    def set_pid(self, channel, p, i, d, set_point):
        cmd = f"{self.pid_executable} {channel} {p} {i} {d} {set_point}"
        asyncio.run(self.send_command(cmd))

    def clear_pid(self):
        cmd = self.clear_executable
        asyncio.run(self.send_command(cmd))
