'''Directory and instance execution auxiliar functions'''
import datetime
import os
import numpy as np
import pandas as pd

import plotly.express as px

from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.algorithms.moo.spea2 import SPEA2

from pymoo.operators.crossover.pntx import TwoPointCrossover
from pymoo.operators.mutation.bitflip import BitflipMutation
from pymoo.operators.sampling.rnd import BinaryRandomSampling
from pymoo.optimize import minimize
from pymoo.termination import get_termination

from gurobi_bi_objective_generalized_diversity_problem import solve_cdp_epsilon
from structure import instance
from utils.results import OutputHandler
from utils.logger import load_logger

logging = load_logger(__name__)


def execute_instance(path: str, results: OutputHandler) -> float:
    '''
    Reads an instance, iterates to find solutions using GRASP algorithm, evaluates the solutions,
    identifies non-dominated solutions, computes execution time, and saves results.

    Args:
      path (str): represents the path to the instance that needs to be solved. This path is used
    to read the instance data and save the results later on with the same name.
      config (dict): contains the configuration settings for the algorithm.
      results (OutputHandler): contains methods for handling and displaying the output of the
    algorithm, such as generating plots and saving results to files with the ID number of the
    execution number of each instance.

    Returns:
      (float): returns the total execution time in seconds.
    '''
    result_table = pd.DataFrame(columns=['Solution', 'MaxSum', 'MaxMin', 'Cost', 'Capacity'])

    logging.info('Solving instance %s:', path)

    inst = instance.read_instance(path)
    dist_matrix = np.array(inst['d'])  # Distance matrix

    costs = np.array(inst['a'])  # Costs for each node
    capacities = np.array(inst['c'])  # Capacities for each node
    B = inst['B']  # Minimum required capacity
    K = inst['K']  # Maximum allowed budget

    start = datetime.datetime.now()



    result_table = solve_cdp_epsilon(result_table, dist_matrix, costs, capacities, B, K)

    print(result_table)
    results.save(result_table, datetime.datetime.now() - start, [], '', path, "Gurobi")
    #
    # else:
    #     logging.warning('No solution found for %s', path)
    #
    #     results.save(result_table, secs, [], '', path, algo)


def execute_directory(directory: str):
    '''
    Scans a directory for text files, executes instances with specified configurations, and saves
    the results in a CSV file.

    Args:
      directory (str): represents the path to the directory where the files (instances) are located.
      config (dict): contains the configuration settings for the algorithm.
    '''
    with os.scandir(directory) as files:
        ficheros = [file.name for file in files if file.is_file() and file.name.endswith(".txt")]

    results = OutputHandler()

    for f in ficheros:
        path = os.path.join(directory, f)
        execute_instance(path, results)
