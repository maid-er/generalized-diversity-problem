'''GRASP execution function (construction and LS calls)'''
import copy
import datetime

from constructives import biased_randomized
from local_search import variable_neighborhood_descent
from structure.solution import Solution

from utils.logger import load_logger

logging = load_logger(__name__)


def execute(inst: dict, config: dict, preprocess:bool, combination: tuple, combinations_dict_alpha:dict, iteration: int, results_dict, start, rng) -> Solution:
    '''The function executes a GRASP algorithm with a specified number of iterations and a given
    beta value, selecting the best solution found during the iterations.

    Args:
      inst (dict): a dictionary containing the instance data. The dictionary includes the number of
    nodes `n`, the number of nodes to be selected `p`, a distance matrix `d` representing the
    distances from each node to the rest of the nodes, a cost vector `a` with the costs of each
    node, and a capacity vector `a` with the capacities of each node.
      config (dict): contains the construction and local search strategies defined by the user in
    the config file.
      objective (int): ID of the objective considered for this iteration. {0: MaxSum, 1: MaxMin}.

    Returns:
        (Solution): the solution found.
    '''
    # Get config parameters

    # print('Executing GRASP algorithm with: ')
    # print('\tBiased construction with parameters %s', parameters)
    # print('\t%s Local Search strategy following the %s Improve scheme',
    #       ls_strategy, ls_scheme)

    alpha_interval = combinations_dict_alpha[combination]

    alpha = rng.uniform(alpha_interval[0], alpha_interval[1])

    # Construction phase (Biased GRASP)
    if combination[0] == "C":
        solution_list, combination = biased_randomized.construct(inst, config, combination, alpha, start, rng)
    else:
        solution_list, combination = biased_randomized.deconstruct(inst, config, combination, alpha, start, rng)

    if len(solution_list) == 0:
        return [], []
    c_sol_list = [s.clone() for s in solution_list]
    # Local Search phase
    ls_sols = [0]
    if len(solution_list) > 1:
        ls_sols = [0, -1]

    if preprocess:
        for solution_pre in solution_list:
            solution_pre_clone = solution_pre.clone()

            results_dict.append({"solution": solution_pre_clone, "iteration": iteration, "combination": combination, "alpha": alpha, "ls": False})

    else:
        for sol in [solution_list[i] for i in ls_sols]:  # Apply LS only to 1st and last solutions
            if len(sol.solution_set) > 0:  # Ensure a solution is constructed
                variable_neighborhood_descent.improve(sol, config)
                time_solution = datetime.datetime.now() - start
                sol.time = round(time_solution.total_seconds(), 2)

    return c_sol_list, solution_list

