'''
Auxiliar function to apply Best Improve Local Search.
Objective functions selected and unselected elements are compared iteratively. All the
neighborhood is explored, and the exchange between elements (selected-unselected) that
offers the best improvement is performed.
'''
import datetime
from itertools import combinations

from constructives.biased_randomized import create_candidate_list
from structure.dominance import exchange_is_dominant
from structure.instance import get_all_pairwise_distances
from structure.solution import Solution

from utils.logger import load_logger

logging = load_logger(__name__)


# TODO IMPLEMENT ALT LOCAL SEARCH STRATEGY

def try_improvement(sol: Solution, objective: int = 0,
                    switch: list = [1, 1], max_time: int = 5) -> bool:
    '''Attempts to improve a solution by selecting and interchanging a selected element (node)
    with an unselected element. The improvement is obtained if the new solution dominates the
    previous solution.

    Args:
      sol (Solution): contains the solution information.
      objective (int): the objective function by which the selected and unselected nodes are
    sorted.
      switch (list): indicates the neighborhood being analized in the local search. The first
    element defines how many nodes will be removed from the solution and the second element
    determines the number of nodes that will be added to the solution. Defaults to [1, 1] for
    a standard 1-1 exchange.
      max_time (int): maximum local search execution time in seconds. If no improvement is find
    in this time, the local search is stopped.

    Returns:
      (bool): `True` if the improvement was successful (i.e., if the objective values are
    dominant and constraints are met with the interchange), and `False` otherwise.
    '''
    (worst_selected,
     sel_maxsum_variability, sel_maxmin,
     best_unselected,
     unsel_maxsum_variability, unsel_maxmin) = select_exchange(sol, objective, switch, max_time)

    # Make exchange if new solution dominates old solution
    new_dominates_old = exchange_is_dominant(sel_maxsum_variability, sel_maxmin,
                                             unsel_maxsum_variability, unsel_maxmin)
    if new_dominates_old:
        for v in best_unselected:
            sol.add_to_solution(v, unsel_maxmin, unsel_maxsum_variability)
        for u in worst_selected:
            sol.remove_from_solution(u, sel_maxmin, sel_maxsum_variability)
        return True
    return False


def select_exchange(sol: Solution, objective: int, switch: list, max_time: int = 5):
    '''Interchanges the worst element in solution (lowest sum of distances to the rest of the
    selected elements) with the best unselected element (highest sum of distances to the rest
    of the selected elements).

    Args:
      sol (Solution): contains the solution information.
      switch (list): indicates the neighborhood being analized in the local search. The
    first element defines how many nodes will be removed from the solution and the second
    element determines the number of nodes that will be added to the solution.

    Returns:
      sel (int): worst selected element ID.
      best_sum_sel (float): sum of distances from `sel` to the rest of the elements in solution.
      best_min_sel (float): minimum distance from `sel` to the rest of the elements in solution.
      unsel (int): best unselected element ID.
      best_sum_unsel (float): sum of distances from `unsel` to the rest of the elements in
    solution.
      best_min_unsel (float): minimum distance from `unsel` to the rest of the elements in
    solution.
    '''
    selected, unselected = create_selected_unselected(sol, objective)
    # Select the first combination of size switch[0] in current solution and the first combination
    # of size switch[1] in unselected candidate list whose exchange makes a dominant new solution
    # that mets the constraints.
    selected_combinations = list(combinations(selected, switch[0]))
    unselected_combinations = list(combinations(unselected, switch[1]))

    sel = -1
    best_sum_sel = 0x3f3f3f3f
    best_min_sel = 0x3f3f3f3f
    unsel = -1
    best_sum_unsel = 0
    best_min_unsel = 0

    start = datetime.datetime.now()
    for combo_s in selected_combinations:
        # If time is exceeded break LS without improvement
        # if datetime.timedelta(seconds=max_time) < datetime.datetime.now() - start:
        #     print('Unable to find an improvement in the established time.')
        #     break

        pairwise_d = get_all_pairwise_distances(sol.instance, combo_s)
        d_sum_s = [sol.distance_sum_to_solution(v) for v in combo_s] + pairwise_d
        d_min_s = [sol.minimum_distance_to_solution(v) for v in combo_s] + pairwise_d
        for combo_u in unselected_combinations:
            # If time is exceeded break LS without improvement
            # if datetime.timedelta(seconds=max_time) < datetime.datetime.now() - start:
            #     print('Unable to find an improvement in the established time.')
            #     break

            pairwise_d = get_all_pairwise_distances(sol.instance, combo_u)
            d_sum_u = [sol.distance_sum_to_solution(v, without=combo_s)
                       for v in combo_u] + pairwise_d
            d_min_u = [sol.minimum_distance_to_solution(v, without=combo_s)
                       for v in combo_u] + pairwise_d

            new_dominates_old = exchange_is_dominant(sum(d_sum_s), min(d_min_s),
                                                     sum(d_sum_u), min(d_min_u))

            if new_dominates_old \
                and sol.satisfies_cost(combo_u, combo_s) \
                    and sol.satisfies_capacity(combo_u, combo_s):

                # Check if this new solution is better than the best exchange found so far
                new_exch_dominates_old = exchange_is_dominant(best_sum_unsel-best_sum_sel,
                                                              sum(d_sum_u)-sum(d_sum_s),
                                                              best_min_unsel,
                                                              min(d_min_u))
                if new_exch_dominates_old:
                    sel = combo_s
                    best_sum_sel = sum(d_sum_s)
                    best_min_sel = min(d_min_s)
                    unsel = combo_u
                    best_sum_unsel = sum(d_sum_u)
                    best_min_unsel = min(d_min_u)

    return sel, best_sum_sel, best_min_sel, unsel, best_sum_unsel, best_min_unsel


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
    # Get only the node ID
    selected = [s[2] for s in selected]
    unselected = [u[2] for u in unselected]

    return selected, unselected
