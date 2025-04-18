'''Auxiliar class to handle candidate solutions'''


class Solution:
    '''Auxiliar class to handle solution information'''
    def __init__(self, instance: dict):
        '''Initialize Solution'''
        self.solution_set = set()
        self.of_MaxSum = 0
        self.of_MaxMin = 0x3f3f3f3f
        self.total_cost = 0
        self.total_capacity = 0
        self.instance = instance

    def clone(self):
        new_sol = Solution(self.instance)
        new_sol.solution_set = self.solution_set
        new_sol.of_MaxMin = self.of_MaxMin
        new_sol.of_MaxSum = self.of_MaxSum
        new_sol.total_cost = self.total_cost
        new_sol.total_capacity = self.total_capacity
        return new_sol

    def add_to_solution(self, u: int, min_distance: float = -1, sum_variation: float = -1):
        '''Updates a solution by adding a specified element and its corresponding value to the
        objective function.

        Args:
          u (int): represents the ID of an element (node) that will be added to the solution.
          min_distance (float): is an optional parameter with a default value of -1. The default
        value -1 is used when the first candidate is added to set.
          sum_variation (float): is an optional parameter with a default value of -1. The default
        value -1 is used when the first candidate is added to sum all the distances from selected
        candidate `u` to the rest of the candidates in the objective function 'of'. Then, each
        time a new candidate is added, the `sum_variation` is received as an input representing the
        sum of the distances from the added element `u` and the rest of the nodes in the solution.
        '''
        if sum_variation == -1 or min_distance == -1:
            for s in self.solution_set:
                distance_u_s = self.instance['d'][u][s]
                self.of_MaxSum += distance_u_s
                if self.of_MaxMin > distance_u_s:
                    self.of_MaxMin = distance_u_s
        else:
            self.of_MaxSum += sum_variation
            if self.of_MaxMin > min_distance:
                self.of_MaxMin = min_distance
        self.total_cost += self.instance['a'][u]
        self.total_capacity += self.instance['c'][u]
        self.solution_set.add(u)

    def remove_from_solution(self, u: int, min_distance: float = -1, sum_variation: float = -1):
        '''Removes an element from a solution and updates the objective function value accordingly.

        Args:
          u (int): represents the ID of an element (node) that will be removed from the solution.
          min_distance (float): is an optional parameter with a default value of -1. The default
        value -1 is used when the first candidate is added to set.
          sum_variation (float): is an optional parameter with a default value of -1. Each time a
        node is removed from the solution, the `ofVariation` is received as an input representing
        the sum of the distances from the removed element `u` and the rest of the nodes in the
        solution.
        '''
        self.solution_set.remove(u)
        if sum_variation == -1 or min_distance == -1:
            for s in self.solution_set:
                distance_u_s = self.instance['d'][u][s]
                self.of_MaxSum -= distance_u_s
                if self.of_MaxMin == distance_u_s:
                    self.of_MaxMin = self.minimum_distance_in_solution()
        else:
            self.of_MaxSum -= sum_variation
            if self.of_MaxMin == min_distance:
                self.of_MaxMin = self.minimum_distance_in_solution()
        self.total_cost -= self.instance['a'][u]
        self.total_capacity -= self.instance['c'][u]

    def contains(self, u: int) -> bool:
        '''Checks if a given candidate ID `u` is present in the current solution attribute
        `solution_set`.

        Args:
          u (int): represents the ID of a candidate element (node).

        Returns:
          (bool): indicates whether the variable `u` is present in the 'sol' key of the dictionary
        `sol`.
        '''
        return u in self.solution_set

    def distance_sum_to_solution(self, u: int, without: list = [-1]) -> float:
        '''Calculates the sum of the distances from a given node to the rest of the nodes in the
        solution graph, excluding the node specified with the optional input `without`.

        Args:
          u (int): represents the ID of the candidate element (node) from which we want to calculate
        the sum of the distances to the rest of the nodes.
          without (list): it is an optional parameter that allows you to specify the ID of the
        node(s) that should be excluded from the calculation of the sum of the distances. If the
        `without` parameter is provided, the function will skip calculating the distance to the
        specified value in the solution.

        Returns:
          (float): returns the sum of the distances from a given node `u` to the rest of the nodes
        in solution `sol`, excluding the distance to a specific node `without` if provided.
        '''
        d = 0
        for s in self.solution_set:
            if s not in without:
                d += self.instance['d'][s][u]
        return round(d, 2)

    def minimum_distance_to_solution(self, u: int, without: list = [-1]) -> float:
        '''Calculates the minimum distance from a given node to the rest of the nodes in the
        solution graph, excluding the node specified with the optional input `without`.

        Args:
          u (int): represents the ID of the candidate element (node) from which we want to find the
        minimum distance to the rest of the nodes.
          without (list): it is an optional parameter that allows you to specify the ID of the
        node(s) that should be excluded from the search of the minimum distance. If the `without`
        parameter is provided, the function will skip calculating the distance to the specified
        value in the solution.

        Returns:
          (float): returns the minimum distance value from a given node `u` to the rest of the
        nodes in solution `sol`, excluding the distance to a specific node `without` if provided.
        '''
        min_d = 0x3f3f3f3f
        for s in self.solution_set:
            if s not in without and s != u:
                d = self.instance['d'][s][u]
                if d < min_d:
                    min_d = d
        return round(min_d, 2)

    def minimum_distance_in_solution(self):
        '''
        The function calculates the minimum pairwise distance between the nodes in the solution.

        Returns:
          (float): the minimum pairwise distance between the nodes in the solution set, rounded to
        two decimal places.
        '''
        min_d = 0x3f3f3f3f
        for s in self.solution_set:
            d = self.minimum_distance_to_solution(s)
            if d < min_d:
                min_d = d
        return round(min_d, 2)

    def is_feasible(self) -> float:
        '''Checks if a solution has at least 2 nodes.

        Returns:
          (bool): indicates whether the length of the solution_set attribute, that is, the selected
        candidates in the solution, is higer than 2.
        '''
        return len(self.solution_set) > 2

    def satisfies_cost(self, u: int = -1, v: int = -1):
        '''Checks if a solution meets the cost constraint.

        Args:
          u (int): it is an optional parameter that allows you to specify the ID of the candidate
        element (node) that might be added to the solution set.
          v (int): it is an optional parameter that allows you to specify the ID of the node that
        might be removed from the solution set.

        Returns:
          (bool): indicates whether the new solution with node `u` added and `v` removed, would
        meet the cost constraint.
        '''
        # removing_candidate = 0
        # if v != -1:
        #     removing_candidate = sol['instance']['a'][v]
        possible_cost = self.total_cost
        if v != -1:
            for q in v:
                possible_cost -= self.instance['a'][q]
        if u != -1:
            for q in u:
                possible_cost += self.instance['a'][q]

        return possible_cost < self.instance['K']

    def satisfies_capacity(self, u: int = -1, v: int = -1):
        '''Checks if a solution meets the capacity constraint.

        Args:
          u (int): it is an optional parameter that allows you to specify the ID of the candidate
        element (node) that might be added to the solution set.
          v (int): it is an optional parameter that allows you to specify the ID of the node that
        might be removed from the solution set.

        Returns:
          (bool): indicates whether the new solution with node `u` added and `v` removed, would
        meet the capacity constraint.
        '''
        possible_capacity = self.total_capacity
        if v != -1:
            for q in v:
                possible_capacity -= self.instance['c'][q]
        if u != -1:
            for q in u:
                possible_capacity += self.instance['c'][q]

        return possible_capacity > self.instance['B']
