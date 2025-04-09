'''
Auxiliar function to apply First Improve Local Search.
Objective functions selected and unselected elements are compared iteratively,
when the unselected element's result improves the selected one's, they are interchanged
in the solution.
'''
from itertools import combinations

from constructives.biased_randomized import create_candidate_list
from structure.dominance import exchange_is_dominant
from structure.instance import get_all_pairwise_distances
from structure.solution import Solution

from utils.logger import load_logger

logging = load_logger(__name__)


def try_improvement(sol: Solution, objective: int, improvement_criteria: str,
                    switch: list = [1, 1]) -> bool:
    '''Attempts to improve a solution by selecting and interchanging a selected element (node)
    with an unselected element. The improvement is obtained if the new solution dominates the
    previous solution.

    Args:
      sol (Solution): contains the solution information.
      objective (int): ID of the objective considered for this iteration. {0: MaxSum, 1: MaxMin}.
      improvement_criteria (str): criteria used to consider that the new solution obtained with the
    exchange improves the previous one. It can be 'Dom', where the new solution must dominate the
    previous one to be better, or 'Alt', where if the new solution improves the last one in the
    objective function value in `objective`, an improvement will be assumed.
      switch (list): indicates the neighborhood being analized in the local search. The first
    element defines how many nodes will be removed from the solution and the second element
    determines the number of nodes that will be added to the solution. Defaults to [1, 1] for
    a standard 1-1 exchange.

    Returns:
      (bool): `True` if the improvement was successful (i.e., if the objective values are
    dominant and constraints are met with the interchange), and `False` otherwise.
    '''
    selected, unselected = create_selected_unselected(sol, objective)

    # Filter only possible dominant solutions for both objectives
    for constraint_objective in [0, 1]:
        worst_selected_constraint = min([s[constraint_objective] for s in selected])
        # If the objective is MaxSum, we can't know if switching 1 node for 2 unselected
        # nodes with lower values will result in a lower sum, so don't discard them
        if not (constraint_objective == 0 and switch[0] < switch[1]):
            unselected = [u for u in unselected
                          if u[constraint_objective] >= worst_selected_constraint]
        else:
            # TODO añadir para caso MaxSum y switch 1-2
            pass

    # First Improvement strategy:
    # Select the first combination of size switch[0] in current solution and the first combination
    # of size switch[1] in unselected candidate list whose exchange makes a dominant new solution
    # that mets the constraints.

    # Build all the possible combinations of switch[0] elements among the selected nodes
    selected_combinations = list(combinations(selected, switch[0]))
    # Build all the possible combinations of switch[1] elements among the unselected nodes
    unselected_combinations = list(combinations(unselected, switch[1]))
    # Filter only combinations with a higher pairwise distance than current solution's MaxMin
    if switch[1] > 1:
        unselected_combinations = [combo_u for combo_u in unselected_combinations
                                   if min(get_all_pairwise_distances(sol.instance,
                                                                     [u[2] for u
                                                                      in combo_u])) > sol.of_MaxMin]

    # For all the possible combinations between the selected elements
    for combo_s in selected_combinations:
        nodes_s = [s[2] for s in combo_s]  # Get node IDs
        # Pairwise distances between all the nodes in combo_s
        pairwise_d = get_all_pairwise_distances(sol.instance, nodes_s)
        # Negative pairwise distance because it is considered twice (if there are 2 nodes)
        d_sum_s = [s[0] for s in combo_s] + [-d for d in pairwise_d]
        d_min_s = [s[1] for s in combo_s]  # + pairwise_d
        # For all the possible combinations between the unselected elements
        for combo_u in unselected_combinations:
            nodes_u = [u[2] for u in combo_u]  # Get node IDs
            # If the constraints are not met with the new combo, try new exchange
            if not (sol.satisfies_cost(nodes_u, nodes_s)
                    and sol.satisfies_capacity(nodes_u, nodes_s)):
                continue
            # Pairwise distances between all the nodes in combo_u
            pairwise_d = get_all_pairwise_distances(sol.instance, nodes_u)
            # Calculate d_sum_u for each node in combo_u removing the potential removed nodes in
            # combo_s from solution
            d_sum_u = [u[0] - sum([sol.instance['d'][u[2]][s[2]] for s in combo_s])
                       for u in combo_u] + pairwise_d
            # Calculate d_min_u for each node in combo_u without considering the potential removed
            # nodes in combo_s
            d_min_u = [sol.minimum_distance_to_solution(v[2], without=nodes_s)
                       for v in combo_u] + pairwise_d

            # TODO IMPROVE CODE
            # Check if new solution improves the latest depending on the selected criteria
            if improvement_criteria == 'Dom':
                new_improves_old = exchange_is_dominant(sum(d_sum_s), min(d_min_s),
                                                        sum(d_sum_u), min(d_min_u))
            else:
                if objective == 0:
                    new_improves_old = sum(d_sum_s) < sum(d_sum_u)
                else:
                    new_improves_old = min(d_min_s) < min(d_min_u)

            if new_improves_old:
                # Remove worst selected node(s) from solution
                for s in nodes_s:
                    sol.remove_from_solution(s)
                # Add best unselected node(s) to solution
                for u in nodes_u:
                    sol.add_to_solution(u)

                return True
    return False


def create_selected_unselected(sol: Solution, objective: int):
    '''Takes a solution instance as input and returns two lists - one containing selected items
    and the other containing unselected items based on the solution. The selected elements are
    sorted in reverse order according to the objective function. Meanwhile, the unselected
    elements are sorted from the best candidate to the worst.

    Args:
      sol (Solution): contains the solution information.

    Returns:
      selected (list): contains the candidates selected in the current solution.
      unselected (list): contains the unselected candidates in the current solution.
    '''
    cl = create_candidate_list(sol)

    selected = []
    unselected = []

    for v in cl:
        if sol.contains(v[2]):
            selected.append(v)
        else:
            unselected.append(v)

    selected.sort(key=lambda row: row[objective])  # Sort from worst to best
    unselected.sort(key=lambda row: -row[objective])  # Sort from best to worst

    return selected, unselected
