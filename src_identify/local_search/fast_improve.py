'''
Auxiliar function to apply Fast Improve Local Search.
The worst selected element and best unselected element are interchanged to improve
the initial solution.
'''
from itertools import combinations

from structure.dominance import exchange_is_dominant
from structure.instance import get_all_pairwise_distances
from structure.solution import Solution
from utils.logger import load_logger

logging = load_logger(__name__)


def try_improvement(sol: Solution, objective: int, switch: int = [1, 1]) -> bool:
    '''Attempts to improve a solution by selecting and interchanging a selected element (node)
    with an unselected element. The improvement is obtained if the new solution dominates the
    previous solution.

    Args:
      sol (Solution): contains the solution information.
      switch (list): indicates the neighborhood being analized in the local search. The
    first element defines how many nodes will be removed from the solution and the second
    element determines the number of nodes that will be added to the solution. Defaults to
    [1, 1] for a standard 1-1 exchange.

    Returns:
      (bool): `True` if the improvement was successful (i.e., if the objective values are
    dominant and constraints are met with the interchange), and `False` otherwise.
    '''
    (worst_selected,
     sel_maxsum_variability, sel_maxmin,
     best_unselected,
     unsel_maxsum_variability, unsel_maxmin) = select_exchange(sol, switch)

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


def select_exchange(sol: Solution, switch: list):
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
    n = sol.instance['n']
    sel = -1
    best_sum_sel = 0x3f3f3f3f
    best_min_sel = 0x3f3f3f3f
    unsel = -1
    best_sum_unsel = 0
    best_min_unsel = 0
    # For every element combination of size switch[0] in current solution, select the
    # one with the worst objective function values
    for combo in combinations(sol.solution_set, switch[0]):
        pairwise_d = get_all_pairwise_distances(sol.instance, combo)
        d_sum = [sol.distance_sum_to_solution(v) for v in combo] + pairwise_d
        d_min = [sol.minimum_distance_to_solution(v) for v in combo] + pairwise_d
        if sum(d_sum) <= best_sum_sel and min(d_min) <= best_min_sel:
            best_sum_sel = sum(d_sum)
            best_min_sel = min(d_min)
            sel = list(combo)

    # For every element combination of size switch[1] in unselected candidate list, select
    # the one with the best objective function values
    for combo in combinations(range(n), switch[1]):
        if not any(sol.contains(v) for v in combo):
            pairwise_d = get_all_pairwise_distances(sol.instance, combo)
            d_sum = [sol.distance_sum_to_solution(v, without=sel) for v in combo] + pairwise_d
            d_min = [sol.minimum_distance_to_solution(v, without=sel) for v in combo] + pairwise_d
            # Check if OFs of the new element(s) are better than the one(s) selected so far and
            # if constraints are met. If True, change best unselected element(s).
            if sum(d_sum) >= best_sum_unsel and min(d_min) >= best_min_unsel \
                and sol.satisfies_cost(combo, sel) \
                    and sol.satisfies_capacity(combo, sel):

                best_sum_unsel = sum(d_sum)
                best_min_unsel = min(d_min)
                unsel = list(combo)

    return sel, best_sum_sel, best_min_sel, unsel, best_sum_unsel, best_min_unsel
