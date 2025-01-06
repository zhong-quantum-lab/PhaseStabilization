import numpy as np
import matplotlib.pyplot as plt

lambda_nm = 1550e-9  # Wavelength in meters
alpha_T = 5e-7  # Thermal expansion coefficient
L1 = 1000
L2 = L1
def DeltaT(t):
    return np.random.normal(0, 0.5)

def L1t(t):
    return L1 * (1 + alpha_T * t)

def L2t(t):
    return L2
    #return L2 * (1 + alpha_T * DeltaT(t))

def PeriodShift(t):
    return (L1t(t) - L2t(t))* 1e6

temp = np.linspace(0, 1, 1000)  # Time from 0 to 100 seconds with 1000 points
phase_drift = np.array([PeriodShift(t) for t in temp])

# Plot phase drift over time
plt.figure(figsize=(10, 6))
plt.plot(temp, phase_drift, label="Phase Drift")
plt.xlabel("Temperature Delta")
plt.ylabel("Length difference in um")
plt.title("Phase Drift Due to Environmental Fluctuations")
plt.legend()
plt.grid()
plt.show()