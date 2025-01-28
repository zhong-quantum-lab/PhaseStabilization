import numpy as np
import matplotlib.pyplot as plt

# Define the ranges for R1 and R2
r1_min, r1_max = 0, .9
r2_min, r2_max = 0, .9

# Create a grid of R1 and R2 values
r1 = np.linspace(r1_min, r1_max, 500)
r2 = np.linspace(r2_min, r2_max, 500)
R1, R2 = np.meshgrid(r1, r2)

# Compute the equation (1-R1)/(2-R1-R2)^2
# Avoid division by zero by setting a very small value where the denominator is zero
denominator = (2 - R1 - R2)**2
denominator[denominator == 0] = np.nan  # Set invalid values to NaN
Z = np.log((1 - R1) / denominator)

# Mask out any invalid values for better visualization
Z = np.ma.masked_invalid(Z)

# Plot the heatmap
plt.figure(figsize=(8, 6))
c = plt.pcolormesh(R1, R2, Z, shading='auto', cmap='viridis')
plt.colorbar(c, label='Log (1-R_1)/(2-R_1-R_2)^2')
plt.xlabel('$R_1$')
plt.ylabel('$R_2$')
plt.title('Heatmap of $(1-R_1)/(2-R_1-R_2)^2$')
plt.tight_layout()
plt.show()
