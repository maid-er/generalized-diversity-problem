import pyomo.environ as pyo
import numpy as np
import pandas as pd

def solve_cdp_epsilon(result_table, dist_matrix, costs, capacities, B, K):
    """
    Multiobjective CDP using ε-constraint method.
    - Objective 1: maximize sum of pairwise distances (diversity)
    - Objective 2: maximize dmin (minimum pairwise distance among selected nodes)
      handled as a constraint: dmin >= epsilon
    """

    n = len(costs)
    M = np.max(dist_matrix)
    epsilons = sorted(set(np.unique(dist_matrix[dist_matrix > 0])))
    # epsilons = [0,50,100]
    for eps in epsilons:
        model = pyo.ConcreteModel()
        model.I = pyo.RangeSet(0, n - 1)

        # Decision variables
        model.x = pyo.Var(model.I, domain=pyo.Binary)
        model.dmin = pyo.Var(domain=pyo.NonNegativeReals)

        # Objective: maximize diversity
        def obj_rule(model):
            return sum(dist_matrix[i, j] * model.x[i] * model.x[j]
                       for i in model.I for j in model.I if i < j)
        model.obj = pyo.Objective(rule=obj_rule, sense=pyo.maximize)

        # Constraints
        model.cost_con = pyo.Constraint(expr=sum(costs[i] * model.x[i] for i in model.I) <= K)
        model.cap_con = pyo.Constraint(expr=sum(capacities[i] * model.x[i] for i in model.I) >= B)

        # Distance consistency constraints
        model.def_dmin = pyo.ConstraintList()
        for i in model.I:
            for j in model.I:
                if i != j:
                    model.def_dmin.add(
                        model.dmin <= dist_matrix[i, j] + M * (2 - model.x[i] - model.x[j])
                    )

        # ε-constraint for dmin
        model.eps_con = pyo.Constraint(expr=model.dmin >= eps)

        # Solve
        solver = pyo.SolverFactory('gurobi')
        solver.options['TimeLimit'] = 600
        results_solver = solver.solve(model, tee=False)
        # --- Check feasibility ---
        status = results_solver.solver.status
        termination = results_solver.solver.termination_condition

        if (status == pyo.SolverStatus.ok and
            termination == pyo.TerminationCondition.optimal) or \
                termination == pyo.TerminationCondition.feasible:
            # Feasible solution found
            selected_nodes = [i for i in model.I if pyo.value(model.x[i]) > 0.5]
            diversity_val = pyo.value(model.obj)
            dmin_val = pyo.value(model.dmin)
            print(diversity_val, dmin_val)
            total_cost = sum(costs[i] for i in selected_nodes)
            total_capacity = sum(capacities[i] for i in selected_nodes)

            # Append row to DataFrame
            result_table.loc[len(result_table)] = {
                'Solution': selected_nodes,
                'MaxSum': diversity_val,
                'MaxMin': dmin_val,
                'Cost': total_cost,
                'Capacity': total_capacity
            }
        else:
            # Skip infeasible solutions
            print(f"⚠️  Infeasible for epsilon = {eps}, stopping...")
            break

    # --- Eliminate dominated solutions ---
    if not result_table.empty:
        result_table = remove_dominated(result_table)

    return result_table

def remove_dominated(df):
    """
    Removes dominated solutions (Pareto filtering)
    Keeps only non-dominated ones based on MaxSum and MaxMin.
    """
    df = df.copy().reset_index(drop=True)
    keep = []

    for i in range(len(df)):
        dominated = False
        for j in range(len(df)):
            if i != j:
                if (df.loc[j, 'MaxSum'] >= df.loc[i, 'MaxSum'] and
                        df.loc[j, 'MaxMin'] >= df.loc[i, 'MaxMin'] and
                        (df.loc[j, 'MaxSum'] > df.loc[i, 'MaxSum'] or
                         df.loc[j, 'MaxMin'] > df.loc[i, 'MaxMin'])):
                    dominated = True
                    break
        if not dominated:
            keep.append(i)

    return df.loc[keep].reset_index(drop=True)
