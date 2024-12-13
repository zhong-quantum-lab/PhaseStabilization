import numpy as np
import paramiko
import matplotlib.pyplot as plt

# Define the PID range
PID_RANGE = (-2**13, 2**13)
def evaluate_policy(pid_vals, ssh, remote_csv_path="/root/acquisition_data.csv",
                    local_csv_path="acquisition_data.csv"):
        # Step 1: Run the PID executable with the PID parameters
        pid_command = f"/root/pid {int(pid_vals[0])} {int(pid_vals[1])} {int(pid_vals[2])}"
        stdin, stdout, stderr = ssh.exec_command(pid_command)
        stdout.read().decode()
        stderr.read().decode()

        # Step 2: Run the signal capture executable
        capture_command = "/root/capture_signal"
        stdin, stdout, stderr = ssh.exec_command(capture_command)
        stdout.read().decode()
        stderr.read().decode()

        # Step 3: Retrieve the CSV file via SCP
        with ssh.open_sftp() as sftp:
            sftp.get(remote_csv_path, local_csv_path)
        print(f"File successfully copied to {local_csv_path}")

        # Step 4: Calculate reward based on signal stability
        signal_data = np.loadtxt(local_csv_path, delimiter=",")
        reward = -np.std(signal_data)  # Negative standard deviation as reward
        return reward


def initialize_population(pop_size, pid_range):
    """
    Initialize a population of PID parameter sets.
    """
    return np.random.uniform(pid_range[0], pid_range[1], size=(pop_size, 3))

def mutate(pid_params, mutation_rate, pid_range):
    """
    Apply mutation to a set of PID parameters.
    """
    mutated = pid_params + mutation_rate * np.random.normal(size=pid_params.shape)
    return np.clip(mutated, pid_range[0], pid_range[1])  # Keep within bounds

def crossover(parent1, parent2):
    """
    Perform crossover between two parents to produce an offspring.
    """
    alpha = np.random.uniform(0, 1, size=parent1.shape)
    return alpha * parent1 + (1 - alpha) * parent2

def genetic_algorithm(ssh, pop_size=50, generations=100, mutation_rate=0.1):
    """
    Genetic algorithm to optimize PID parameters.
    """
    # Initialize population
    population = initialize_population(pop_size, PID_RANGE)
    best_rewards = []
    best_params = None

    for generation in range(generations):
        # Evaluate the population
        rewards = np.array([evaluate_policy(pid, ssh) for pid in population])
        sorted_indices = np.argsort(rewards)[::-1]  # Sort by reward (descending)
        population = population[sorted_indices]    # Sort population by fitness
        rewards = rewards[sorted_indices]

        # Track the best parameters
        if best_params is None or rewards[0] > best_rewards[-1]:
            best_params = population[0]
        best_rewards.append(rewards[0])

        # Print progress
        print(f"Generation {generation + 1}: Best Reward = {rewards[0]}")

        # Select top performers for mating
        top_k = pop_size // 2
        parents = population[:top_k]

        # Generate next generation
        next_gen = []
        for _ in range(pop_size):
            indices = np.random.choice(len(parents), size=2, replace=False)  # Randomly choose 2 indices
            parent1, parent2 = parents[indices]  # Select parents using the indices

            offspring = crossover(parent1, parent2)
            offspring = mutate(offspring, mutation_rate, PID_RANGE)
            next_gen.append(offspring)
        population = np.array(next_gen)

    # Return the best solution
    return best_params, best_rewards

def main():
    # Connection details
    red_pitaya_host = "205.208.56.192"
    red_pitaya_user = "root"
    red_pitaya_password = "root"

    # Initialize SSH connection
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(red_pitaya_host, username=red_pitaya_user, password=red_pitaya_password)
    print("SSH connection established.")

    try:
        # Run the genetic algorithm
        best_params, best_rewards = genetic_algorithm(ssh, pop_size=30, generations=10, mutation_rate=0.14)

        print(f"Optimal PID Parameters: {best_params}")

        # Plot the best reward over generations
        plt.plot(best_rewards, label="Best Reward")
        plt.title("Genetic Algorithm Optimization")
        plt.xlabel("Generation")
        plt.ylabel("Reward")
        plt.legend()
        plt.grid(True)
        plt.show()

    finally:
        ssh.close()
        print("SSH connection closed.")

if __name__ == "__main__":
    main()
