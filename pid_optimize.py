from remote_streaming import RP_Streamer
from remote_pid import RP_Pid
import numpy as np
import pygad
import matplotlib.pyplot as plt

# Define your setup
pid_pitaya_ip = "205.208.56.215"
capture_pitaya_ip = "10.120.12.220"
captures = 1000
setpoint = 4096  # Configurable setpoint

# Initialize the streamer and PID controller
streamer = RP_Streamer(capture_pitaya_ip)
# streamer.set_decimation(2 ** 17)
pid = RP_Pid(pid_pitaya_ip)
pid.clear_pid()

# Capture initial unstable signal
# data_unstable, samplerate = streamer.capture_signal(captures)

# List to store fitness values
fitness_history = []


def fitness_func(ga_instance, solution, solution_idx):
    kp, ki, kd = solution  # Extract parameters
    print(f"Generation: {ga_instance.generations_completed}, Solution Index: {solution_idx}")
    pid.set_pid(int(kp), int(ki), int(kd), setpoint)
    data_stable, _ = streamer.capture_signal(captures)

    setpoint_mapped = setpoint / (2 ** 14)
    mse = np.mean((data_stable - setpoint_mapped) ** 2)
    fitness = 1 / mse  # Optimize for lower mse

    print(f"MSE: {mse:.6f}, Fitness: {fitness:.6f}\n")
    print("-----------------------------------------")

    # Store fitness value
    fitness_history.append(fitness)

    return fitness


num_generations = 15
num_parents_mating = 5
sol_per_pop = 10
num_genes = 3

# Define parameter ranges
init_range_low = -8096
init_range_high = 8096

ga_instance = pygad.GA(
    num_generations=num_generations,
    num_parents_mating=num_parents_mating,
    fitness_func=fitness_func,
    sol_per_pop=sol_per_pop,
    num_genes=num_genes,
    init_range_low=init_range_low,
    init_range_high=init_range_high,
    parent_selection_type="sss",
    keep_parents=3,
    crossover_type="single_point",
    mutation_type="random",
    mutation_num_genes=1
)

# Run the genetic algorithm
ga_instance.run()

# Retrieve best solution
solution, solution_fitness, solution_idx = ga_instance.best_solution()
print(f"Best PID parameters: {solution}")
print(f"Best fitness value: {solution_fitness}")

# Apply best solution to the PID controller
pid.set_pid(*solution, setpoint)
data_stable, _ = streamer.capture_signal(captures)

# Plot fitness history
plt.figure()
plt.plot(fitness_history, marker='o', linestyle='-')
plt.xlabel("Trial")
plt.ylabel("Fitness Value")
plt.title("Fitness Evolution Over Trials")
plt.grid()
plt.show()
