from remote_streaming import RP_Streamer
from remote_pid import RP_Pid
import numpy as np
import pygad
import matplotlib.pyplot as plt
import os

# Define your setup
pid_pitaya_ip = "rp-f0cace.local"
capture_pitaya_ip = "10.120.12.217"
captures = 100000
setpoint = 4096  # Configurable setpoint

# Create log directory
log_dir = "pid_optimization_log"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "fitness_log.txt")

# Initialize the streamer and PID controller
streamer = RP_Streamer(capture_pitaya_ip)
pid = RP_Pid(pid_pitaya_ip)
pid.clear_pid()

# Capture initial unstable signal
# data_unstable, samplerate = streamer.capture_signal(captures)

# List to store fitness values
fitness_history = []


def fitness_func(ga_instance, solution, solution_idx):
    kp11, ki11, kd11, kp21, ki21, kd21  = map(lambda x: int(x), solution) # Extract parameters
    pid.set_pid(11, kp11, ki11, kd11, setpoint)
    pid.set_pid(21, kp21, ki21, kd21, setpoint)
    data_stable, rate = streamer.capture_signal(captures)
    distance = (data_stable - (setpoint / 8192)) ** 2
    derivative = (data_stable[1:] - data_stable[0:-1])**2
    fitness = -1*(np.sum(distance) + np.sum(derivative))
    plt.figure(figsize=(8, 6))
    time = [i/rate for i in range(len(data_stable))]
    plt.plot(time, data_stable)
    plt.xlabel("Time")
    plt.ylabel("Signal")
    plt.title(f"Generation={ga_instance.generations_completed}, Solution Index={solution_idx}, Fitness={fitness}")
    plt.ylim(0, 1)
    plt.grid()
    path = log_dir + f"/Generation_{ga_instance.generations_completed}"
    os.makedirs(path, exist_ok=True)
    filename = f"Idx_{solution_idx}.png"
    plt.savefig(f"{path}/{filename}")
    plt.close()
    print("-----------------------------------------")
    log_entry = f"Generation: {ga_instance.generations_completed}, Solution Index: {solution_idx}, PID11: ({kp11}, {ki11}, {kd11}), PID21: ({kp21}, {ki21}, {kd21})  Fitness: {fitness:.6f}\n"
    print(log_entry)

    fitness_history.append(fitness)
    plt.plot(fitness_history)
    plt.savefig(f"{log_dir}/fitness.png")
    plt.close()
    with open(log_file, "a") as f:
        f.write(log_entry)

    return fitness


num_generations = 25
num_parents_mating = 6
sol_per_pop = 12  # Total population size
num_genes = 6  # Number of parameters being optimized

# Define parameter-specific ranges
param_ranges = np.array([
    [-8195, 8195],   # Gene 1 range
    [-2000, 2000],      # Gene 2 range
    [-100, 100], # Gene 3 range
    [-8195, 8195],    # Gene 4 range
    [-2000, 2000], # Gene 5 range
    [-100, 100]      # Gene 6 range
])

# Manually define a few initial members
manual_solutions = np.array([
    [8000, 500, 0, -2000, 0, 20]])

# Generate the rest of the population randomly within specified ranges
num_random_solutions = sol_per_pop - manual_solutions.shape[0]
random_solutions = np.array([
    np.random.uniform(low=param_ranges[i, 0], high=param_ranges[i, 1], size=num_random_solutions)
    for i in range(num_genes)
]).T

initial_population = np.vstack((manual_solutions, random_solutions))

ga_instance = pygad.GA(
    num_generations=num_generations,
    num_parents_mating=num_parents_mating,
    fitness_func=fitness_func,
    sol_per_pop=sol_per_pop,
    num_genes=num_genes,
    initial_population=initial_population,  # Custom initial population
    parent_selection_type="rws",
    keep_parents=4,
    crossover_type="single_point",
    mutation_type="random",
    mutation_num_genes=2
)

# Run the GA
ga_instance.run()

# Retrieve best solution
solution, solution_fitness, solution_idx = ga_instance.best_solution()
print(f"Best PID parameters: {solution}")
print(f"Best fitness value: {solution_fitness}")

# Apply best solution to the PID controller
pid.set_pid(*solution, setpoint)
data_stable, _ = streamer.capture_signal(captures)

plt.figure()
plt.plot(fitness_history, marker='o', linestyle='-')
plt.xlabel("Trial")
plt.ylabel("Fitness Value")
plt.title("Fitness Evolution Over Trials")
plt.grid()

plot_path = os.path.join(log_dir, "fitness_plot.png")
plt.savefig(plot_path)
plt.show()

print(f"Log saved to: {log_file}")
print(f"Plot saved to: {plot_path}")