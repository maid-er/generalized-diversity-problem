'''Auxiliar functions to construct a Biased-Randomized solution'''
import copy
import math
import random

from structure.solution import Solution

from utils.logger import load_logger

logging = load_logger(__name__)

OBJECTIVE_FUNCTIONS = {0: 'MaxSum',
                       1: 'MaxMin'}

w1, w2 = 0.7, 0.3


def construct(inst: dict, config: dict, objective: int) -> Solution:
    '''The function constructs a solution for a given instance using a Biased Greedy Randomized
    Adaptive Search (B-GRASP) procedure with specified parameters.

    Args:
      inst (dict): a dictionary containing the instance data. The dictionary includes the number of
    nodes `n`, the number of nodes to be selected `p`, and a distance matrix `d` representing the
    distances from each node to the rest of the nodes.
      config (dict): always contains a 'mo_approach_C' key that indicates the strategy used in the
    construction phase to adapt the GRASP algorithm to the multi-objective problem. Additionally,
    it contains a 'distibution' key that indicates the probability distribution that will be used
    to biase the node selection from the candidate list. If the distribution is geometric, it
    contains another 'beta' key with the its parameter, which determines the trade-off between
    exploration and exploitation in the construction of a solution. The closer 'beta' is from 0,
    the more uniform random will be the selection, thus, the construction will have a more
    exploratory behavior. If 'beta' is closer to 1, a greedier solution will be constructed.
      objective (int): ID of the objective considered for this iteration. {0: MaxSum, 1: MaxMin}.

    Returns:
        (Solution): contains the solution information.
    '''
    # Get config parammeters
    mo_construction_approach = config.get('mo_approach_C')
    distribution = config.get('parameters').get('distribution')

    solution_list = []

    sol = Solution(inst)  # Initialize solution
    n = inst['n']
    u = random.randint(0, n-1)  # Select first node
    sol.add_to_solution(u)
    cl = create_candidate_list(sol, u)
    while sol.satisfies_cost() and len(cl) > 0:
        # If the approach is to alternate objectives IN each construction,
        # switch objective in each iteration, else maintain the (input) objective
        # set by the strategy to alternate objectives BETWEEN constructions.
        if mo_construction_approach == 'AltInS':
            objective = len(cl) % 2  # 0: MaxSum, 1: MaxMin

        # Filter only nodes that provide a feasible solution
        cl = [c for c in cl if sol.satisfies_cost([c[2]])]
        if len(cl) == 0:  # If the cost won't be met with any new element
            break
        if objective == 0:
            if random.random()< 0.5:
                cl.sort(key=lambda row: -row[3])
            else:
                cl.sort(key=lambda row: -row[objective])

        else:
            cl.sort(key=lambda row: -row[objective])
        #print('Sorted biased candidate list with %s objective.', OBJECTIVE_FUNCTIONS.get(objective))

        # Biased Randomization to select new node to add to solution
        if distribution == 'Geometric':
            beta = config.get('parameters').get('beta')
            beta = beta if beta >= 0 else random.random()
            selIdx = int(math.log(random.random()) / math.log(1 - beta))
            selIdx = selIdx % len(cl)
        elif distribution == 'Triangular':
            selIdx = int(len(cl) * (1 - math.sqrt(random.random())))

        # Add selected node to solution
        cSel = cl[selIdx]
        sol.add_to_solution(cSel[2], cSel[1], cSel[0])
        cl.remove(cSel)
        update_candidate_list(sol, cl, added=cSel[2])

        # If solution is feasible, save it in the solution list
        if sol.satisfies_capacity() and sol.satisfies_cost():
            solution_list.append(sol.clone())

    # Check if any feasible solution is constructed
    if len(solution_list) == 0:
        # logging.error('No feasible solution reached in the construction phase.')
        sol = Solution(inst)
        sol.of_MaxMin = 0
        solution_list.append(sol)

    return solution_list


def deconstruct(inst: dict, config: dict, objective: int) -> Solution:
    '''The function constructs a solution for a given instance using a Biased Greedy Randomized
    Adaptive Search (B-GRASP) procedure with specified parameters.

    Args:
      inst (dict): a dictionary containing the instance data. The dictionary includes the number of
    nodes `n`, the number of nodes to be selected `p`, and a distance matrix `d` representing the
    distances from each node to the rest of the nodes.
      config (dict): always contains a 'mo_approach_C' key that indicates the strategy used in the
    construction phase to adapt the GRASP algorithm to the multi-objective problem. Additionally,
    it contains a 'distibution' key that indicates the probability distribution that will be used
    to biase the node selection from the candidate list. If the distribution is geometric, it
    contains another 'beta' key with the its parameter, which determines the trade-off between
    exploration and exploitation in the construction of a solution. The closer 'beta' is from 0,
    the more uniform random will be the selection, thus, the construction will have a more
    exploratory behavior. If 'beta' is closer to 1, a greedier solution will be constructed.
      objective (int): ID of the objective considered for this iteration. {0: MaxSum, 1: MaxMin}.

    Returns:
        (Solution): contains the solution information.
    '''
    # Get config parammeters
    mo_construction_approach = config.get('mo_approach_C')
    distribution = config.get('parameters').get('distribution')

    solution_list = []

    sol = Solution(inst)  # Initialize solution
    n = inst['n']
    # Generate initial solution set with all the nodes
    for u in range(n):
        sol.add_to_solution(u)
    cl = create_candidate_list(sol)
    while sol.satisfies_capacity() and len(cl) > 0:
        # If the approach is to alternate objectives IN each construction,
        # switch objective in each iteration, else maintain the (input) objective
        # set by the strategy to alternate objectives BETWEEN constructions.
        if mo_construction_approach == 'AltInS':
            objective = len(cl) % 2  # 0: MaxSum, 1: MaxMin

        # Filter only nodes that provide a feasible solution
        cl = [c for c in cl if sol.satisfies_capacity(v=[c[2]])]
        if len(cl) == 0:  # If the capacity won't be met with any new element
            break
        if objective == 0:
            cl.sort(key=lambda row: row[3])
        else:
            cl.sort(key=lambda row: row[objective])
        #print('Sorted biased candidate list with %s objective.', OBJECTIVE_FUNCTIONS.get(objective))

        # Biased Randomization to select new node to add to solution
        if distribution == 'Geometric':
            beta = config.get('parameters').get('beta')
            beta = beta if beta >= 0 else random.random()
            selIdx = int(math.log(random.random()) / math.log(1 - beta))
            selIdx = selIdx % len(cl)
        elif distribution == 'Triangular':
            selIdx = int(len(cl) * (1 - math.sqrt(random.random())))

        # Add selected node to solution
        cSel = cl[selIdx]
        sol.remove_from_solution(cSel[2], cSel[1], cSel[0])
        cl.remove(cSel)
        update_candidate_list(sol, cl, removed=cSel[2])

        # If solution is feasible, save it in the solution list
        if sol.satisfies_capacity() and sol.satisfies_cost():
            solution_list.append(sol.clone())

    # Check if any feasible solution is constructed
    if len(solution_list) == 0:
        # logging.error('No feasible solution reached in the construction phase.')
        sol = Solution(inst)
        sol.of_MaxMin = 0
        solution_list.append(sol)

    return solution_list


def create_candidate_list(sol: Solution, first: int = -1) -> list:
    '''The function creates a list of candidate solutions based on the distance to the given
    solution and excluding the first candidate.

    Args:
      sol (Solution): contains the solution information.
      first (int): represents the ID of the first candidate element (node) in the solution. This
    index is used to exclude the first candidate from the candidate list that is being created.

    Returns:
      (list): a list of candidate solutions. Each candidate solution is represented as a list
    containing the sum of the distances to the rest of the nodes in the solution and the index
    of the candidate solution. It defaults to -1 when the objective values of every candidates
    need to be calculated.
    '''
    n = sol.instance['n']
    cl = []
    for c in range(n):
        if c != first:
            d_sum = sol.distance_sum_to_solution(c)
            d_min = sol.minimum_distance_to_solution(c)
            cl.append([d_sum, d_min, c])

    cl = calculate_custom_maxsum_objective_function(sol, cl)

    return cl


def update_candidate_list(sol: Solution, cl: list, added: int = -1, removed: int = -1):
    '''Iterates through a candidate list and updates the first (sum of distances) and second
    (minimum distance) elements of each candidate adding the distance to the new `added` element.

    Args:
      sol (Solution): contains the solution information.
      cl (list): a list of candidate solutions. Each candidate solution is represented as a list
    containing the sum of the distances and the minimum distance to the rest of the nodes in the
    solution, and the index of the candidate solution.
      added (int): represents the ID of the candidate that was added to the solution. Defaults to
    -1 when no candidate is added.
      removed (int): represents the ID of the candidate that was removed from the solution.
    Defaults to -1 when no candidate is removed.
    '''
    for i in range(len(cl)):
        c = cl[i]

        if added != -1:
            c_to_added_distance = sol.instance['d'][added][c[2]]

            # Update MaxSum objective value
            c[0] += c_to_added_distance
            # Update MaxMin objective value
            # If the distance to the added is lower than current MaxMin
            if c_to_added_distance < c[1]:
                c[1] = c_to_added_distance

        if removed != -1:
            c_to_removed_distance = sol.instance['d'][removed][c[2]]

            # Update MaxSum objective value
            c[0] -= c_to_removed_distance
            # Update MaxMin objective value
            # If the distance to the removed is equal to current MaxMin
            if c_to_removed_distance == c[1]:
                c[1] = sol.minimum_distance_to_solution(c[2])

    if len(cl) > 0:
        cl = calculate_custom_maxsum_objective_function(sol, cl)


def calculate_custom_maxsum_objective_function(sol: Solution, cl: list):
    # Extract values separately
    dsum_values = [item[0] for item in cl]
    cost_values = [sol.instance['a'][c[2]] for c in cl]
    cap_values = [sol.instance['c'][c[2]] for c in cl]

    # Compute min and max
    dsum_min, dsum_max = min(dsum_values), max(dsum_values)
    cost_min, cost_max = min(cost_values), max(cost_values)
    cap_min, cap_max = min(cap_values), max(cap_values)

    # Normalize using min-max scaling
    normalized_dsum = []
    normalized_cost = []
    normalized_cap = []
    for i in range(len(cl)):
        normalized_dsum.append((dsum_values[i] - dsum_min) / (dsum_max - dsum_min) if dsum_max != dsum_min else 0)
        normalized_cost.append((cost_values[i] - cost_min) / (cost_max - cost_min) if cost_max != cost_min else 0)
        normalized_cap.append((cap_values[i] - cap_min) / (cap_max - cap_min) if cap_max != cap_min else 0)

    # Add new weighted MaxSum value to candidate list
    cl = [
        [
            cl[i][0],
            cl[i][1],
            cl[i][2],  # Keep the ID unchanged
            -normalized_cost[i]
        ]
        for i in range(len(cl))
    ]

    return cl
