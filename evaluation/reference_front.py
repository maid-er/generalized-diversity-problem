import os
import pandas as pd


def calculate_reference_front(result_dir, set, subset, inst):
    '''Calculate reference solution set R'''
    configurations = os.listdir(result_dir)

    all_solution_table = pd.DataFrame(columns=['Solution', 'MaxSum', 'MaxMin', 'Cost', 'Capacity'])
    # Read all the solutions for this instance in a unique DataFrame
    for config in configurations:
        if config.endswith('.csv') or config.endswith('.html'):
            continue

        config_path = os.path.join(result_dir, config, set, subset, inst)
        executions = os.listdir(config_path)
        for exec in executions:
            solutions = pd.read_csv(os.path.join(config_path, exec))
            if exec != 'add_data.csv':
                all_solution_table = all_solution_table.append(solutions)
    # Find non-dominated solutions among all constructions
    all_solution_table = all_solution_table.reset_index(drop=True)
    if all_solution_table.Solution.isnull().all():
        return pd.DataFrame()

    is_non_dominated = get_nondominated_solutions(all_solution_table.reset_index())
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


def get_nondominated_solutions(all_solutions: pd.DataFrame) -> list:
    '''
    Identifies non-dominated solutions within a table of solutions.
    '''
    is_non_dominated = [True] * len(all_solutions)
    for i, sol_i in all_solutions.iterrows():
        for j, sol_j in all_solutions.iterrows():
            if i != j and solution_is_dominant(sol_j, sol_i):
                is_non_dominated[i] = False
                break

    return is_non_dominated
