import numpy as np

from pymoo.core.problem import Problem


# Custom problem class: Bi-objective diversity model with cost and capacity constraints
class BiObjectiveGeneralizedDiversityProblem(Problem):

    def __init__(self, dist_matrix, costs, capacities, B, K):
        n = dist_matrix.shape[0]  # Number of nodes

        # Define the number of variables (n nodes) and number of objectives (2)
        super().__init__(n_var=n,
                         n_obj=2,
                         n_constr=2,  # Two constraints: cost and capacity
                         xl=0,
                         xu=1,
                         type_var=bool)

        # Save distance matrix, costs, capacities, budget (K), and required capacity (B)
        self.dist_matrix = dist_matrix
        self.costs = costs
        self.capacities = capacities
        self.B = B  # Minimum capacity
        self.K = K  # Maximum budget

    def _evaluate(self, X, out, *args, **kwargs):
        # Objectives: Max-Sum and Max-Min
        f1 = []
        f2 = []

        # Constraints
        g1 = []  # Total cost must be <= K
        g2 = []  # Total capacity must be >= B

        for x in X:
            # Get indices of selected elements (where x[i] == 1)
            selected = np.where(x == 1)[0]

            if len(selected) > 1:
                # Max-Sum: Sum of pairwise distances between selected elements
                sum_dist = np.sum([self.dist_matrix[i, j]
                                   for i in selected for j in selected if i < j])
                f1.append(-sum_dist)  # Multiply by -1 to maximize

                # Max-Min: Minimum distance between selected elements
                min_dist = np.min([self.dist_matrix[i, j]
                                   for i in selected for j in selected if i != j])
                f2.append(-min_dist)  # Multiply by -1 to maximize
            else:
                # If fewer than 2 elements are selected, the solution is invalid
                f1.append(float("inf"))
                f2.append(float("inf"))

            # Constraint 1: Total cost must be <= K
            total_cost = np.sum(self.costs[selected])
            g1.append(total_cost - self.K)

            # Constraint 2: Total capacity must be >= B
            total_capacity = np.sum(self.capacities[selected])
            g2.append(self.B - total_capacity)

        # Set the objective values
        out["F"] = np.column_stack([f1, f2])

        # Set the constraint violations (must be <= 0 to satisfy constraints)
        out["G"] = np.column_stack([g1, g2])
