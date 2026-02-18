import csv
import random
import os
import subprocess
import time
import pandas as pd
import matplotlib.pyplot as plt
from deap import base, creator, tools, algorithms
from scenario_wrapper import run_follow_leading_vehicle

# --- GA Setup ---
POPULATION_SIZE = 6
NUM_GENERATIONS = 3

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("attr_speed", random.uniform, 20, 30)
toolbox.register("attr_distance", random.uniform, 5, 10)
toolbox.register("individual", tools.initCycle, creator.Individual,
                 (toolbox.attr_speed, toolbox.attr_distance), n=1)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# --- Fitness Function ---
def fitness_function(individual):
    speed, distance = round(individual[0], 2), round(individual[1], 2)

    # Set environment variables for scenario_runner
    env = os.environ.copy()
    env["LEADING_VEHICLE_SPEED"] = str(speed)
    env["LEADING_VEHICLE_LOCATION"] = str(distance)

    print(f"Speed: {speed}, Distance: {distance} → ", end='')

    try:
        result = subprocess.run(
            ["python3", "scenario_runner.py", "--scenario", "FollowLeadingVehicle_1", "--waitForEgo"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120
        )

        output = result.stdout.decode("utf-8") + result.stderr.decode("utf-8")
        if "Collision" in output:
            print("Fitness: 0.0")
            return (0.0,)
        else:
            print("Fitness: 1.0")
            return (1.0,)

    except subprocess.TimeoutExpired:
        print("Timeout → Fitness: 0.0")
        return (0.0,)

toolbox.register("evaluate", fitness_function)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("mate", tools.cxBlend, alpha=0.5)
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=5, indpb=0.2)

# --- CSV Setup ---
csv_file = "scenario_results.csv"
write_header = not os.path.exists(csv_file)
csv_out = open(csv_file, mode="a", newline="")
csv_writer = csv.writer(csv_out)
if write_header:
    csv_writer.writerow(["Generation", "Speed", "Distance", "Fitness"])

# --- Run Optimization ---
population = toolbox.population(n=POPULATION_SIZE)

for gen in range(NUM_GENERATIONS):
    print(f"\n--- Generation {gen + 1} ---")
    offspring = algorithms.varAnd(population, toolbox, cxpb=0.5, mutpb=0.2)

    fits = []
    for ind in offspring:
        fitness = toolbox.evaluate(ind)
        ind.fitness.values = fitness
        csv_writer.writerow([gen + 1, ind[0], ind[1], fitness[0]])
        fits.append(fitness[0])
        time.sleep(5)  # Give time for system reset

    population = toolbox.select(offspring, k=len(population))
    best = tools.selBest(population, k=1)[0]
    print(f"Best of Gen {gen + 1}: Speed={best[0]:.2f}, Distance={best[1]:.2f}, Fitness={best.fitness.values[0]}")

csv_out.close()

# --- Plotting ---
df = pd.read_csv(csv_file)
colors = df["Fitness"].map({1.0: "green", 0.0: "red"})

plt.figure(figsize=(8, 6))
plt.scatter(df["Speed"], df["Distance"], c=colors, alpha=0.7)
plt.xlabel("Lead Vehicle Speed (m/s)")
plt.ylabel("Distance to Ego Vehicle (m)")
plt.title("Scenario Outcomes: Safe (green) vs Unsafe (red)")
plt.grid(True)
plt.tight_layout()
plt.savefig("scenario_outcomes_plot.png")
plt.show()

