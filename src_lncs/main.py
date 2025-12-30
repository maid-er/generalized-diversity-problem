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

    path = os.path.join('instances', 'Test_set', 'GKD-c')

    tasks = []
    for config in config_list:

        # rng = random.Random(7357)
        # execution.execute_directory(path, config, rng, 7357)
        #
        betas = [-1, 0.25, 0.75]
        # modes = ["Alt-Btw-3FO", "Alt-Btw", "Alt-Btw-LC"]
        modes = [[0.5, "Alt-Btw-LC"]]
        for mode in modes:
            config["parameters"]["beta"] = mode[0]
            config["mo_approach_C"] = mode[1]
            rng = random.Random(7357)
            execution.execute_directory(path, config, rng, 7357)

    # os.remove(os.path.join('temp', 'execution.txt'))
