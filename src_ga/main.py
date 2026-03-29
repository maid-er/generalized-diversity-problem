'''Main function'''
from concurrent.futures import ProcessPoolExecutor
import os
import random
random.seed(7357)

from utils import execution
from utils.logger import load_logger

logging = load_logger(__name__)


def run_experiment(args):
    path, seed = args
    execution.execute_directory(path, seed)


if __name__ == "__main__":
    print("Initializing Genetic algorithms...")

    path = os.path.join('instances', 'All_Instances', 'All_Instances')

    tasks = []

    for n in range(10):
        seed = 7357 + n
        tasks.append((path, seed))

    with ProcessPoolExecutor() as executor:
        executor.map(run_experiment, tasks)

    # os.remove(os.path.join('temp', 'execution.txt'))
