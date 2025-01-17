import numpy as np
import matplotlib.pyplot as plt

# Constants
c = 3e8  # Speed of light (m/s)
center_wavelength = 1550e-9  # Center wavelength (m)
center_frequency = c / center_wavelength  # Central frequency (Hz)
linewidth = 1e3  # Linewidth (Hz)

def simulate_phase_noise(delta_L, num_steps, timestep):
    gamma = linewidth / 2  # Half-width at half-maximum (Hz)
    time = np.linspace(0, num_steps * timestep, num_steps)
    freq_noise = gamma * np.random.standard_cauchy(size=num_steps)
    phase_noise = 2 * np.pi * (center_frequency + freq_noise) * timestep * (delta_L / c)
    return time, phase_noise

# Parameters
delta_L = 10  # Path length difference (meters)
num_steps = 100000  # Number of steps in the simulation
timestep = 1e-10  # Time step (seconds)

# Run simulation
time, phase_noise = simulate_phase_noise(delta_L, num_steps, timestep)

# Plot results
plt.figure(figsize=(10, 6))
plt.plot(time, phase_noise, label=f"Phase Noise (ΔL = {delta_L} m)")
plt.xlabel("Time (s)")
plt.ylabel("Phase Noise (radians)")
plt.title("Simulated Phase Noise")
plt.grid()
plt.legend()
plt.show()
