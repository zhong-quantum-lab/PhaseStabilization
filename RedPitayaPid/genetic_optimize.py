import numpy as np
import os
import matplotlib.pyplot as plt
import rp
# Define the PID parameter range
PID_RANGE = (-2**13, 2**13)


def evaluate_policy(pid_vals, csv_path="/root/acquisition_data.csv"):
    try:
        # Step 1: Run the PID executable with the PID parameters
        pid_command = f"/root/pid {int(pid_vals[0])} {int(pid_vals[1])} {int(pid_vals[2])}"
        os.system(pid_command)  # Execute the PID control command
        iterations = 20 
        reward = [0 for i in range(iterations)]
        for i in range(iterations):
            signal = capture_signal()
            reward[i] = -np.std(signal)
        reward = np.mean(reward)
        with open("genetic_log.txt", "a") as file:
            print(f"    {pid_command}, reward = {reward}")
            file.write(f" {pid_command}, reward = {reward}\n")
        return reward

    except Exception as e:
        print(f"Error during evaluation: {e}")
        return -float('inf')  # Return a large negative reward for failure



def capture_signal(num_buffers=10, buffer_size=16384, decimation=rp.RP_DEC_2, trigger_level=0.5):
    try:
        # Initialize the Red Pitaya API
        rp.rp_Init()

        # Configure acquisition settings
        rp.rp_AcqReset()
        rp.rp_AcqSetDecimation(decimation)
        rp.rp_AcqSetTriggerLevel(rp.RP_T_CH_1, trigger_level)
        rp.rp_AcqSetTriggerDelay(0)  # Set trigger delay
        rp.rp_AcqSetGain(rp.RP_CH_1, rp.RP_LOW)  # Set channel gain
        rp.rp_AcqStart()  # Start acquisition

        # Allocate space for all data
        all_data = np.zeros(num_buffers * buffer_size, dtype=float)

        for buffer_index in range(num_buffers):
            # Trigger the acquisition
            rp.rp_AcqStart()  # Start continuous acquisition
            rp.rp_AcqSetTriggerSrc(rp.RP_TRIG_SRC_NOW)

            # Wait for the trigger
            while True:
                trig_state = rp.rp_AcqGetTriggerState()[1]
                if trig_state == rp.RP_TRIG_STATE_TRIGGERED:
                    break

            # Wait for the buffer to be filled
            while True:
                if rp.rp_AcqGetBufferFillState()[1]:
                    break

            # Read data into the corresponding part of the array
            temp_buffer = rp.fBuffer(buffer_size)
            rp.rp_AcqGetDataV(rp.RP_CH_1, 0, buffer_size, temp_buffer)

            # Copy data into the larger array
            start_idx = buffer_index * buffer_size
            end_idx = start_idx + buffer_size
            all_data[start_idx:end_idx] = [temp_buffer[i] for i in range(buffer_size)]

        return all_data

    except Exception as e:
        print(f"Error during acquisition: {e}")
        return None

    finally:
        # Release the Red Pitaya resources
        rp.rp_Release()


def initialize_population(pop_size, pid_range):
    # Sample from three normal distributions
    p_params = np.clip(np.random.normal(0, 2**12, pop_size),-2**13, 2**13)
    i_params = np.clip(np.random.normal(0, 2**12, pop_size),-2**13, 2**13)
    d_params = np.clip(np.random.normal(0, 2**8, pop_size),-2**13, 2**13)
    
    # Combine into a population of shape (pop_size, 3)
    return np.column_stack((p_params, i_params, d_params))


def mutate(pid_params, mutation_rate, pid_range):
    mutated = pid_params + mutation_rate  * np.random.normal(size=pid_params.shape)
    return np.clip(mutated, pid_range[0], pid_range[1])  # Keep within bounds


def crossover(parent1, parent2):
    alpha = np.random.uniform(0, 1, size=parent1.shape)
    return alpha * parent1 + (1 - alpha) * parent2


def genetic_algorithm(pop_size=4, generations=10, mutation_rate=50):
    # Initialize population
    population = initialize_population(pop_size, PID_RANGE)
    best_rewards = []
    best_params = None

    for generation in range(generations):
        # Evaluate the population
        rewards = np.array([evaluate_policy(pid) for pid in population])
        sorted_indices = np.argsort(rewards)[::-1]  # Sort by reward (descending)
        population = population[sorted_indices]    # Sort population by fitness
        rewards = rewards[sorted_indices]

        # Track the best parameters
        if best_params is None or rewards[0] > max(best_rewards, default=float('-inf')):
            best_params = population[0]
        best_rewards.append(rewards[0])

        # Print progress

        with open("genetic_log.txt", "a") as file:
            print(f"Generation {generation + 1}: Best Reward = {rewards[0]}")
            file.write(f"Generation {generation + 1}: Best Reward = {rewards[0]}\n")
        # Select top performers for mating
        top_k = pop_size // 2
        parents = population[:top_k]

        # Generate next generation
        next_gen = []
        for _ in range(pop_size):
            indices = np.random.choice(len(parents), size=2, replace=False)  # Select two distinct parents
            parent1, parent2 = parents[indices]
            offspring = crossover(parent1, parent2)
            offspring = mutate(offspring, mutation_rate, PID_RANGE)
            next_gen.append(offspring)
        population = np.array(next_gen)

    # Return the best solution
    return best_params, best_rewards


def main():
    # Run the genetic algorithm
    print("Running Optimization")
    with open("genetic_log.txt", "w") as file:
        pass
    best_params, best_rewards = genetic_algorithm(pop_size=15, generations=15, mutation_rate=500)

    with open("genetic_log.txt", "a") as file:
        print(f"Optimal PID Parameters: {best_params}")
        file.write(f"Optimal PID Parameters: {best_params}")


    # Plot the best reward over generations
    plt.plot(best_rewards, label="Best Reward")
    plt.title("Genetic Algorithm Optimization")
    plt.xlabel("Generation")
    plt.ylabel("Reward")
    plt.legend()
    plt.grid(True)
    plt.savefig("Training.png", dpi=300)

if __name__ == "__main__":
    main()

