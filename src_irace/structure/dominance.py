'''Auxiliar functions to find non-dominated solutions'''
from structure.solution import Solution


def exchange_is_dominant(sel_maxsum_variability: float, sel_maxmin: float,
                         unsel_maxsum_variability: float, unsel_maxmin: float) -> bool:
    '''
    Checks if selected element(s) is dominated by unselected element(s). A solution
    is dominated if another solution is no worse in all objectives and better in at
    least one.

    Args:
      best_sum_sel (float): sum of distances from `sel` to the rest of the elements in solution.
      best_min_sel (float): minimum distance from `sel` to the rest of the elements in solution.
      best_sum_unsel (float): sum of distances from `unsel` to the rest of the elements in
    solution.
      best_min_unsel (float): minimum distance from `unsel` to the rest of the elements in
    solution.

    Returns:
      (bool): indicates whether the selected element(s) `sel` are dominated by unselected
    element(s) `unsel`.
    '''
    condition1 = all([sel_maxsum_variability <= unsel_maxsum_variability,
                      sel_maxmin <= unsel_maxmin])

    condition2 = any([sel_maxsum_variability < unsel_maxsum_variability,
                      sel_maxmin < unsel_maxmin])

    return condition1 and condition2


def solution_is_dominant(sol1: Solution, sol2: Solution) -> bool:
    '''
    Checks if `sol2` is dominated by `sol1`. A solution is dominated if another solution
    is no worse in all objectives and better in at least one.

    Args:
      sol1 (Solution): contains the objective function values of the solution 1.
      sol2 (Solution): contains the objective function values of the solution 2.

    Returns:
      (bool): indicates whether the `sol2` is dominated by `sol1`.
    '''
    if sol1.of_MaxSum >= sol2.of_MaxSum and sol1.of_MaxMin >= sol2.of_MaxMin:
        # Check if sol1 is strictly better in at least one
        if sol1.of_MaxSum > sol2.of_MaxSum or sol1.of_MaxMin > sol2.of_MaxMin:
            return True


def get_nondominated_solutions(all_solutions: list) -> list:
    n = len(all_solutions)
    if n == 0: return []

    # 1. Track original indices and sort by MaxSum descending, then MaxMin descending
    # This ensures that for any i < j, sol_i is already "better or equal" in MaxSum
    indexed_sols = sorted(
        enumerate(all_solutions),
        key=lambda x: (x[1].of_MaxSum, x[1].of_MaxMin),
        reverse=True
    )

    is_non_dominated = [True] * n
    current_max_min = -float('inf')

    # 2. Linear scan (O(n log n) total due to sorting)
    # Because they are sorted by MaxSum, a solution can only be non-dominated
    # if its MaxMin is strictly better than the best MaxMin seen so far.
    for i, (original_idx, sol) in enumerate(indexed_sols):
        if sol.of_MaxMin > current_max_min:
            # This is a new non-dominated point
            current_max_min = sol.of_MaxMin
        elif sol.of_MaxMin == current_max_min:
            # Handle cases with identical values
            # We need to check if it's strictly worse in MaxSum than the one that set current_max_min
            # But due to sorting, if MaxMin is equal, MaxSum must be <=.
            # Only non-dominated if MaxSum is also equal.
            prev_sol = indexed_sols[i - 1][1]
            if sol.of_MaxSum < prev_sol.of_MaxSum:
                is_non_dominated[original_idx] = False
        else:
            is_non_dominated[original_idx] = False

    return is_non_dominated
#
# def get_nondominated_solutions(all_solutions: list) -> list:
#     '''
#     Identifies non-dominated solutions within a list of solutions.
#
#     Args:
#       all_solutions (list): solutions where each solution is represented as a Solution instance.
#
#     Returns:
#       (list of bool): each value indicates whether the corresponding solution in the input list
#     `all_solutions` is non-dominated by any other solution in the list.
#     '''
#     is_non_dominated = [True] * len(all_solutions)
#     for i, sol_i in enumerate(all_solutions):
#         for j, sol_j in enumerate(all_solutions):
#             if i != j and solution_is_dominant(sol_j, sol_i):
#                 is_non_dominated[i] = False
#                 break
#
#     return is_non_dominated
