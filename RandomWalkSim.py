import numpy as np
import matplotlib.pyplot as plt

def generate_gaussian_random_walk(steps, mu=0, sigma=0.1):
    steps = np.random.normal(mu, sigma, steps)
    return np.cumsum(steps)

def simulate_and_count_exceedances(threshold, steps=100000, simulations=1):
    exceedance_counts = []

    for _ in range(simulations):
        # Generate two independent Gaussian random walks
        L1 = generate_gaussian_random_walk(steps)
        L2 = generate_gaussian_random_walk(steps)

        # Compute the difference between the two random walks
        difference = L1 - L2

        # Count the occurrences where the difference exceeds the threshold
        exceedance_count = np.sum(difference > threshold)
        exceedance_counts.append(exceedance_count)

    # Compute exceedance frequency
    average_exceedance_count = np.mean(exceedance_counts)
    exceedance_frequency = average_exceedance_count / steps

    return average_exceedance_count, exceedance_frequency

# Parameters
threshold = 1.5
steps = 1000
simulations = 100

# Run simulation
average_exceedance_count, exceedance_frequency = simulate_and_count_exceedances(threshold, steps, simulations)

print(f"Average exceedance count over {simulations} simulations: {average_exceedance_count}")
print(f"Average exceedance frequency: {exceedance_frequency}")

# Plot an example
L1 = generate_gaussian_random_walk(steps)
L2 = generate_gaussian_random_walk(steps)
plt.figure(figsize=(10, 6))
plt.plot(L1, label="L1 (Random Walk 1)")
plt.plot(L2, label="L2 (Random Walk 2)")
plt.plot((L1 - L2)% 2, label="L1 - L2 (Difference)", linestyle="--")
plt.axhline(threshold, color="red", linestyle="--", label=f"Threshold ({threshold})")
plt.legend()
plt.xlabel("Step")
plt.ylabel("Value")
plt.title("Gaussian Random Walks and Difference")
plt.grid()
plt.show()
