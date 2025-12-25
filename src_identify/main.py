'''Main function'''
from concurrent.futures import ProcessPoolExecutor
import os
import random
random.seed(7357)

from utils import execution
from utils.config import read_config
from utils.logger import load_logger

logging = load_logger(__name__)

config_list = read_config('config')

def run_experiment(args):
    path, config, seed = args
    rng = random.Random(seed)
    execution.execute_directory(path, config, rng, seed)


if __name__ == "__main__":
    print("Initializing diversity maximization algorithm...")

    path = os.path.join('instances', 'Test_set', 'Test_set')

    tasks = []
    for config in config_list:

        rng = random.Random(7357)
        execution.execute_directory(path, config, rng, 7357)
    #
    #     for n in range(config.get('experiments')):
    #         seed = 7357 + n
    #         tasks.append((path, config, seed))
    #
    # with ProcessPoolExecutor() as executor:
    #     executor.map(run_experiment, tasks)

    # os.remove(os.path.join('temp', 'execution.txt'))
