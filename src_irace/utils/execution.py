'''Directory and instance execution auxiliar functions'''
import datetime
import itertools
import os

import numpy as np
import pandas as pd

from algorithms import grasp
from constructives.biased_randomized import create_candidate_list
from structure import instance
from structure.solution import Solution

from utils.results import OutputHandler
from utils.logger import load_logger
import matplotlib.pyplot  as plt

from structure import dominance
from collections import defaultdict
import statistics
from pymoo.indicators.hv import HV
logging = load_logger(__name__)

def execute_instance(path: str, config: dict, results: OutputHandler, rng, seed) -> float:
    '''
    Reads an instance, iterates to find solutions using GRASP algorithm, evaluates the solutions,
    identifies non-dominated solutions, computes execution time, and saves results.

    Args:
      path (str): represents the path to the instance that needs to be solved. This path is used
    to read the instance data and save the results later on with the same name.
      config (dict): contains the configuration settings for the algorithm.
      results (OutputHandler): contains methods for handling and displaying the output of the
    algorithm, such as generating plots and saving results to files with the ID number of the
    execution number of each instance.

    Returns:
      (float): returns the total execution time in seconds.
    '''
    # Initialize list and table to save solutions
    all_solutions = []  # Final solutions after the LS stage
    result_table = []
    # print('Solving instance %s:', path)
    # Read instance
    inst = instance.read_instance(path)

    max_time = config.get('execution_limits').get('max_time')
    start = datetime.datetime.now()
    # Construct a solution for the IT defined in config
    results_dict = []
    policies = ["C", "D"]
    cost_focus = [0,1,2,3]
    cost_weight = [0,1,2,3,4,5]
    # cost_focus = [0, 1]
    # cost_weight = [0]

    combinations_focus = list(itertools.product(policies, ["focus"], cost_focus))
    combinations_weight = list(itertools.product(policies, ["weight"], cost_weight))
    combinations = combinations_focus + combinations_weight

    combinations_dict_alpha = {comb: [0, 1] for comb in combinations} # initial value for alpha interval

    # Create the complete solution for deconstruct process, saving time creating one time
    complete_solution = Solution()
    for u in range(inst['n']):
        complete_solution.add_to_solution(inst, u)
    cl_complete_solution = create_candidate_list(complete_solution, inst)

    execute_combinations(config, True, combinations, combinations_dict_alpha, max_time, start,
                             inst, results_dict, all_solutions, result_table, rng, complete_solution, cl_complete_solution)

    if len(all_solutions) == 0:
        return 0

    post_combinations, pf_idx = scan_results(combinations, results_dict, start, config)

    # Eliminate the rest of the all_solutions to save ram
    # results_dict = [results_dict[i] for i in pf_idx if results_dict[i]["combination"] in post_combinations]

    valid_indices = [
        i for i in pf_idx
        if results_dict[i]["combination"] in post_combinations
    ]

    results_dict = [results_dict[i] for i in valid_indices]
    # result_table = [result_table[i] for i in valid_indices]
    # all_solutions = [all_solutions[i] for i in valid_indices]


    #Update the alpha interval for the combinations

    results_alpha = analyze_alpha(results_dict)
    # print(results_alpha)

    if config.get("parameters").get("std_multiplier") != "All":

        for key, value in results_alpha.items():

            combinations_dict_alpha[key] = [ max(0, value["mean"] - config.get("parameters").get("std_multiplier") * value["std"]), min(1, value["mean"] + config.get("parameters").get("std_multiplier") * value["std"] )]

        # print(combinations_dict_alpha)

    # elapsed = datetime.datetime.now() - start
    # secs = round(elapsed.total_seconds(), 2)
    # print('Execution scan$learn time: %s', secs)

    start = datetime.datetime.now()

    # print("Start With VND")
    execute_combinations(config, False, post_combinations, combinations_dict_alpha, max_time, start,
                         inst, results_dict, all_solutions, result_table, rng, complete_solution, cl_complete_solution)

    # Find non-dominated solutions among all constructions

    # 3. Create the DataFrame once outside the loop
    results_data = pd.DataFrame(result_table, columns=[
        'Nodes', 'MaxSum', 'MaxMin', 'Cost', 'Capacity', 'Time'
    ])

    # 4. Proceed with dominance filtering
    is_non_dominated = dominance.get_nondominated_solutions(all_solutions)
    dom_result_table = results_data[is_non_dominated].reset_index(drop=True)

    # Compute execution time
    elapsed = datetime.datetime.now() - start
    secs = round(elapsed.total_seconds(), 2)
    # print('Execution time: %s', secs)

    add_data = {
        'time': [secs],
        'all_sols': [len(all_solutions)],
        'nd_sols': [len(dom_result_table)]
    }

    # Build and plot Pareto Front
    # fig = results.pareto_front(dom_result_table, path)
    # Save table and plot with results
    algorithm_params = (f'IT{config.get("iterations")}'
                        f'_b{config.get("parameters").get("beta")}'
                        f'_{config.get("scheme")[:3]}'
                        # f'_nb{len(config.get("neighborhoods"))}'
                        ).replace('.', '')
    # results.save(dom_result_table, add_data, algorithm_params, path, seed)

    current_pareto_front = dom_result_table[['MaxSum', 'MaxMin']].to_numpy()
    # Calculate hypervolume
    # Si el frente de Pareto está vacío, devolver 0
    if current_pareto_front.size == 0:
        hypervolume = 0
    else:
        ind = HV(ref_point=np.array([0.0, 0.0]))
        # *(-1) porque es un problema de maximización
        try:
            hypervolume = ind((-1) * current_pareto_front)
        except:
            return 0

    # print(hypervolume)

    return hypervolume




def execute_combinations(config, preprocess, combinations,combinations_dict_alpha, max_time, start,
                         inst, results_dict, all_solutions, result_table, rng, complete_solution, cl_complete_solution):

    max_iterations = config.get('iterations') if not preprocess else config.get('pre_iterations') * len(combinations)
    for i in range(max_iterations):
        combination = combinations[i%len(combinations)]
        # print(combination)

        if not preprocess:
            # If time is exceeded stop execution
            if datetime.timedelta(seconds=max_time) < datetime.datetime.now() - start:
                # print('Maximum allowed execution time is exceeded. Total IT: %s', i)
                break

        # Run B-GRASP-VND
        # print(f'Finding solution #{i+1}')
        solution_list = grasp.execute(inst, config, preprocess, combination, combinations_dict_alpha, i, results_dict, start, rng, complete_solution, cl_complete_solution)
        # Save solution set found in this IT
        all_solutions += solution_list

        # Add new solutions to result_table
        # for sol in solution_list:

        # Add new solutions to result_table
        for sol in solution_list:
            selected_nodes = ' - '.join([str(s) for s in sorted(sol.solution_set)])
            # 2. Append a simple list or dict to your collector
            result_table.append([
                selected_nodes,
                round(sol.of_MaxSum, 3),
                round(sol.of_MaxMin, 3),
                sol.total_cost,
                sol.total_capacity,
                sol.time
            ])

def execute_directory(directory: str, config: dict, rng, seed):
    '''
    Scans a directory for text files, executes instances with specified configurations, and saves
    the results in a CSV file.

    Args:
      directory (str): represents the path to the directory where the files (instances) are located.
      config (dict): contains the configuration settings for the algorithm.
    '''
    with os.scandir(directory) as files:
        ficheros = [file.name for file in files if file.is_file() and file.name.endswith(".txt")]

    results = OutputHandler()

    for f in ficheros:
        path = os.path.join(directory, f)
        execute_instance(path, config, results, rng, seed)



def plot_solutions(results_dict, color_map):

    used_labels = set()
    plt.figure()
    for sol in results_dict:
        solution = sol["solution"]
        key = sol["combination"]
        color = color_map[key]
        label_i_comp = 0
        if key[1] != "focus":
            label_i_comp = 1
        # label = f"{key[0]} | {key[1]} | {key[2]}"
        label_i = str((4* label_i_comp + key[2] + 1))
        label = f"$\psi^{key[0]}_{label_i}$"
        if key not in used_labels:
            plt.scatter(solution.of_MaxMin, solution.of_MaxSum, color=color, label=label)
            used_labels.add(key)
        else:
            plt.scatter(solution.of_MaxMin, solution.of_MaxSum, color=color)
        plt.scatter(solution.of_MaxMin, solution.of_MaxSum, color=color)

    plt.xlabel('MaxMin')
    plt.ylabel('MaxSum')
    plt.legend(title="Combinations", loc="upper right")  # ⭐ Legend in top right
    plt.grid(True)
    plt.show()


def pareto_front(points):
    """Return indices of points that belong to the Pareto front (MaxMax)."""
    front = []
    for i, (x_i, y_i) in enumerate(points):
        dominated = False
        for j, (x_j, y_j) in enumerate(points):
            if (x_j >= x_i and y_j >= y_i) and (x_j > x_i or y_j > y_i):
                dominated = True
                break
        if not dominated:
            front.append(i)
    return front

def pareto_front(points):
    front = []
    for i, (x_i, y_i) in enumerate(points):
        dominated = False
        for j, (x_j, y_j) in enumerate(points):
            if (x_j >= x_i and y_j >= y_i) and (x_j > x_i or y_j > y_i):
                dominated = True
                break
        if not dominated:
            front.append(i)
    return front

def pareto_delta_front(points, delta:float):
    front = []
    for i, (x_i, y_i) in enumerate(points):
        dominated = False
        for j, (x_j, y_j) in enumerate(points):
            if (x_j >= x_i * delta and y_j >= y_i * delta ) and (x_j  > x_i * delta or y_j > y_i * delta ):
                dominated = True
                break
        if not dominated:
            front.append(i)
    return front


def compute_global_pareto_stats(results_dict, config):

    # Gather all points
    all_points = []
    all_combos = []

    for sol in results_dict:
        combo = sol["combination"]
        solution = sol["solution"]
        all_points.append((solution.of_MaxMin, solution.of_MaxSum))
        all_combos.append(combo)

    # Compute global Pareto front
    global_pf_idx = set(pareto_delta_front(all_points, delta= config.get("parameters").get("delta")))
    total_pf = len(global_pf_idx)

    # Prepare stats
    combinations = set(all_combos)
    stats = {combo: {"pareto": 0, "percentage": 0.0} for combo in combinations}

    # Count Pareto front points per combination
    for idx in global_pf_idx:
        combo = all_combos[idx]
        stats[combo]["pareto"] += 1

    # Compute percentages relative to global PF
    for combo, s in stats.items():
        if total_pf > 0:
            s["percentage"] = 100 * s["pareto"] / total_pf

    return stats, global_pf_idx, total_pf

def analyze_alpha(pareto_combinations):
    grouped = defaultdict(list)

    for d in pareto_combinations:
        grouped[d["combination"]].append(d["alpha"])


    results = {
        combination: {
            "mean": statistics.mean(values),
            "std": statistics.stdev(values) if len(values) > 1 else 0.0
        }
        for combination, values in grouped.items()
    }
    return results

def scan_results(combinations, results_dict, start, config):
    # Number of combinations
    n = len(combinations)

    # Pick a colormap with enough distinct colors
    cmap = plt.get_cmap("tab20")  # 20 visually distinct colors

    # Create the color map dictionary automatically
    color_map = {combo: cmap(i / n) for i, combo in enumerate(combinations)}

    # plot_solutions(results_dict, color_map)

    stats, pf_idx, total_pf = compute_global_pareto_stats(results_dict, config)

    # print(f"Global PF size = {total_pf}")

    # for combo, s in stats.items():
    #     print(f"{combo}: {s['pareto']} / {total_pf}  → {s['percentage']:.1f}%")

    post_combinations = []
    for combo, s in stats.items():
        if s['percentage'] > config.get("parameters").get("threshold"):
            post_combinations.append(combo)

    elapsed = datetime.datetime.now() - start
    secs = round(elapsed.total_seconds(), 2)
    # print('Execution time preprocess: %s', secs)

    # results_dict_pareto = [plot for plot in results_dict if plot["combination"] in post_combinations]
    # plot_solutions(results_dict, color_map)

    return post_combinations, pf_idx