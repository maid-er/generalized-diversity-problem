import os
import pandas as pd
import numpy as np

def calculate_reference_front(result_dir, set, subset, inst):
    '''Calculate reference solution set R'''
    configurations = os.listdir(result_dir)
    all_solution_table = pd.DataFrame(columns=['Solution', 'MaxSum', 'MaxMin', 'Cost', 'Capacity'])
    all_temp_list = []  # Create one list for EVERYTHING

    for config in configurations:
        if config.endswith('.csv') or config.endswith('.html'):
            continue

        config_path = os.path.join(result_dir, config, set, subset, inst)

        # Safety check: ensure path exists
        if not os.path.exists(config_path):
            continue

        executions = os.listdir(config_path)
        for exec in executions:
            if 'result' in exec:
                solutions = pd.read_csv(os.path.join(config_path, exec))
                solutions = solutions.rename(columns={'Nodes': 'Solution'})
                all_temp_list.append(solutions)  # Add to the master list

    # Move this OUTSIDE the loop (un-indent)
    if all_temp_list:
        all_solution_table = pd.concat(all_temp_list, ignore_index=True)

    all_solution_table = all_solution_table.drop_duplicates(subset=['Solution']).reset_index(drop=True)
    if all_solution_table.Solution.isnull().all():
        return pd.DataFrame()

    is_non_dominated = get_nondominated_solutions(all_solution_table)
    reference_table = all_solution_table[is_non_dominated].reset_index(drop=True)

    return reference_table


def solution_is_dominant(sol1: pd.Series, sol2: pd.Series) -> bool:
    '''
    Checks if `sol2` is dominated by `sol1`. A solution is dominated if another solution
    is no worse in all objectives and better in at least one.

    Args:
      sol1 (Solution): contains the objective function values of the solution 1.
      sol2 (Solution): contains the objective function values of the solution 2.

    Returns:
      (bool): indicates whether the `sol2` is dominated by `sol1`.
    '''
    condition1 = all([sol2.MaxSum <= sol1.MaxSum,
                      sol2.MaxMin <= sol1.MaxMin])

    condition2 = any([sol2.MaxSum < sol1.MaxSum,
                      sol2.MaxMin < sol1.MaxMin])

    return condition1 and condition2



def get_nondominated_solutions(df: pd.DataFrame) -> list:
    if df.empty:
        return []

    # 1. Sort by MaxSum descending, then MaxMin descending
    # We keep the original index to return the boolean mask in the correct order
    df_sorted = df.sort_values(by=['MaxSum', 'MaxMin'], ascending=False)

    # Initialize mask using the original index
    is_non_dominated_mask = pd.Series(False, index=df.index)

    current_max_min = -float('inf')
    last_max_sum = -float('inf')
    last_max_min = -float('inf')

    # 2. Linear scan
    for idx, row in df_sorted.iterrows():
        sol_max_sum = row['MaxSum']
        sol_max_min = row['MaxMin']

        if sol_max_min > current_max_min:
            # New non-dominated point (better MaxMin than all seen before)
            is_non_dominated_mask[idx] = True
            current_max_min = sol_max_min

        elif sol_max_min == current_max_min:
            # If MaxMin is equal, it's only non-dominated if MaxSum
            # is also equal to the previous best (identical points)
            if sol_max_sum == last_max_sum:
                is_non_dominated_mask[idx] = True

        # Track last seen values to handle the 'equal' logic
        last_max_sum = sol_max_sum
        last_max_min = sol_max_min

    # Return as a list of booleans corresponding to the original row order
    return is_non_dominated_mask.tolist()

# def get_nondominated_solutions(all_solutions: pd.DataFrame) -> list:
#     '''
#     Identifies non-dominated solutions within a table of solutions.
#     '''
#     is_non_dominated = [True] * len(all_solutions)
#     for i, sol_i in all_solutions.iterrows():
#         for j, sol_j in all_solutions.iterrows():
#             if i != j and solution_is_dominant(sol_j, sol_i):
#                 is_non_dominated[i] = False
#                 break
#
#     return is_non_dominated
