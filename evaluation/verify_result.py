import os
import sys

import pandas as pd

sys.path.append('src')

from structure import instance
from structure.solution import Solution


SET = 'GKD-b_n50'
SUBSET = 'GKD-b_11_n50_b02_m5_k02'


path = os.path.join('instances', 'GDP', SET, f'{SUBSET}.txt')
inst = instance.read_instance(path)

dom_data = pd.read_csv(os.path.join('output', 'NSGA-II', 'GDP', SET, SUBSET, 'ref_results_3.csv'))

nodes_sol1 = dom_data['Solution'].iloc[0].split(' - ')

sol = Solution(inst)  # Initialize solution
for u in nodes_sol1:
    u = int(u) - 2
    sol.add_to_solution(u)

print(sol.of_MaxSum)
print(sol.of_MaxMin)
print(sol.total_cost)
print(sol.total_capacity)

print(dom_data.iloc[0])
