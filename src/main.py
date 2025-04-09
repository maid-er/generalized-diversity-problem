'''Main function'''
import os
import random

from utils import execution
from utils.config import read_config
from utils.logger import load_logger

logging = load_logger(__name__)

config_list = read_config('config')


random.seed(42)

if __name__ == '__main__':
    print('Initializing diversity maximization algorithm...')

    path = os.path.join('instances', 'GDP', 'GKD-b_n50')

    for config in config_list:
        # execution.execute_instance(path, config)
        for n in range(config.get('experiments')):
            execution.execute_directory(path, config)

        os.remove(os.path.join('temp', 'execution.txt'))
