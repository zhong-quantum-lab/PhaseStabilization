# Red Pitaya Phase Stabilization
This repository contains code for active phase stabilization 
using a Red Pitaya FPGA. Furthermore, this project has the ability to analyze properties of the phase noise in a system.

## Usage
There are two ways to use this repository to stabilize phase. Either by directly writing to the Red Pitaya PID through a terminal. Or through a websocket server connection.

Regardless of mode of operation, the first step is to clone the repository onto the Red Pitaya, then cd into RedPitayaPid/ and run `make pid` followed by `make clear_pid`.

These two files form the core functionality for controlling the PID on the Red Pitaya. The compiled executable `pid` can be invoked to set the onboard PID parameters. Use `pid --help` for more information.

From here if you wish to begin interfacing with the Red Pitaya using the server you must run `python server.py`

