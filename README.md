# br-grasp-for-multi-objective-diversity-problem
This repository contains a Biased GRASP algorithm with VND designed to solve the Bi-Objective Generalized Diversity Problem (BOGDP).

## Development environment

The source code was developed using Python 3.9

## Requirements

The required dependencies are gathered in file ```requirements.txt```. To install them execute the following command:

```python
pip install -r requirements.txt
```

## Configuration
The repository includes a configuration file ```config/config.yaml``` that allows users to manually define several parameters to customize the algorithm's performance. The configuration file includes a list of all the algorithm configurations to be tested in a execution.

For example:

```yaml
- iterations: 100  # Number of constructions
  # Construction stage
  parameters:
    distribution: 'Geometric'  # Triangular or Geometric
    beta: 0.5  # From 0 to 1 // if -1, random selection for each construction
  # Local Improvement stage
  strategy: 'VND'  # Standard, or VND
  neighborhoods:
    1: [1, 1]
    2: [1, 2]
    3: [2, 1]
  scheme: 'First'  # Fast, or First

- iterations: 100  # Number of constructions
  # Construction stage
  parameters:
    distribution: 'Geometric'  # Triangular or Geometric
    beta: -1  # From 0 to 1 // if -1, random selection for each construction
  # Local Improvement stage
  strategy: 'VND'  # Standard, or VND
  neighborhoods:
    1: [1, 1]
  scheme: 'First'  # Fast, or First
```

In this case the B-GRASP with VND algorithm will be executed twice.

In the first place, the algorithm will be configured with a `beta` value of 0.5 and the `neighborhoods` to be explored in the Local Search phase will be a 1-1 switch, 1-2 switch, and 2-1 switch between selected and unselected nodes.

Next, in the second run, the algorithm will find the solutions for the BOCDP with a random `beta` value for each construction, and a standard First Improve Local Search with a 1-1 node exchange.

## Code execution

To initialize the algorithm, run the following command in the project's path:

```console
python .\src\main.py
```

## Code content

The B-GRASP algorithm is executed in ```src/main.py``` and operates through multiple iterations handled in ```src/utils/execution.py```. Each iteration involves two key stages that are called from ```src/algrithms/grasp.py```: **construction** and **improvement**.

A trial solution is generated using a greedy randomized approach during the **construction phase**. Elements are selected based on a greedy function, with the selection process randomized using a geometric distribution to give higher probabilities to the most promising candidates. This distribution is controlled by a parameter named `beta`, which ranges between 0 and 1. When the parameter value is closer to 0, the selection process becomes more uniformly randomized. This stage is coded in ```src/constructives/biased_randomized.py```.

The constructed solution is locally enhanced in the **improvement phase**, typically using a local search method. The scripts related to the local search phase are in ```src/local_search```. In this project the Variable Neighborhood Descent (VND) strategy is used for this stage (```variable_neighborhood_descent.py```), which is based in exploring various neighborhoods in a predetermined, deterministic manner by combining different descent heuristics. The project allows the user to select three approaches for the move operator: in the *First Improvement* approach in ```first_improve.py``` the first movement that results in an improvement is performed, The *Best Improvement* approach in ```best_improve.py``` explores all the possible exchange combinations to perform the best one, and the *Fast Improvement* approach in ```fast_improve.py``` involves exchanging the worst selected node with the best unselected node.


The scripts in ```src/structure``` are helpers to handle the instance and solution data. This directory also contains a script with functions to check if a solution is non-dominated.

The module ```src/utils``` contains useful functions to handle the config file reading, the algorithm's execution, the logs, and saving and plotting the results.


## Output

Upon execution, the algorithm generates the following outputs:

1.	**CSV File:** A file containing the non-dominated solutions found by the algorithm, representing the Pareto Front. The CSV includes columns with the following information for each solution set: the IDs of the selected nodes, the Max-Sum value, the Max-Min value, the total cost, and the total capacity.

    An additional `add_data.csv` file is generated where the running times of the different executions are saved.

2.	**Interactive Plot (optional):** A scatter plot of the Pareto Front that visually represents the objective function values (Max-Sum and Max-Min), with cost and capacity values for each alternative solution displayed in the legend.

These outputs provide the user with multiple optimal solutions and essential information to help select the most suitable option for their specific case.


## Algorithm's perfomance evaluation

```evaluation/``` directory includes the source code to compare and evaluate the Pareto Fronts obtained with different configurations of the algorithm for the same instance set by executing:

```console
python .\evaluation\main.py
```

If the user wants to compare results from an external algorithm, take into account that the structure of the output files should be:

```
output
├── <algorithm+config>
│    └── <set>
│         └── <subset>
│              └── <instance>
│                   ├── add_data.csv
│                   └── <results_i.csv>
└── NSGA-II
     └── GDP
          └── GKD-c
               └── GKD-c_01_n500_b02_m50_k02
                    ├── add_data.csv
                    ├── results_1.csv
                    └── results_2.csv
```

The ```select_tuning_files.py``` script can be executed to randomly select a portion (20% by default) of the instances from every set for the algorithm tuning process.

```console
python .\evaluation\select_tuning_files.py
```

It also contains the ```plot_results.py``` script that plots the Pareto Front of a determinate output CSV file with the solution data by executing:

```console
python .\evaluation\plot_results.py
```
