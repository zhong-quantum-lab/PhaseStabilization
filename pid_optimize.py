from remote_streaming import RP_Streamer
from remote_pid import RP_Pid
import numpy as np
import pygad
import matplotlib.pyplot as plt
import os

# Define your setup
pid_pitaya_ip = "205.208.56.215"
capture_pitaya_ip = "10.120.12.220"
captures = 10000
setpoint = 4096  # Configurable setpoint

# Create log directory
log_dir = "pid_optimization_log"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "fitness_log.txt")

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

    log_entry = f"Generation: {ga_instance.generations_completed}, Solution Index: {solution_idx}, Kp: {kp:.4f}, Ki: {ki:.4f}, Kd: {kd:.4f}, MSE: {mse:.6f}, Fitness: {fitness:.6f}\n"
    print(log_entry)
    print("-----------------------------------------")

    # Store fitness value
    fitness_history.append(fitness)

    # Save log entry to file
    with open(log_file, "a") as f:
        f.write(log_entry)

    return fitness


num_generations = 50
num_parents_mating = 4
sol_per_pop = 8
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
    keep_parents=1,
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

# Save plot to file
plot_path = os.path.join(log_dir, "fitness_plot.png")
plt.savefig(plot_path)
plt.show()

print(f"Log saved to: {log_file}")
print(f"Plot saved to: {plot_path}")