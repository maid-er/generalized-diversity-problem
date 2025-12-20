'''Main function'''
import os
import random
random.seed(7357)

from utils import execution
from utils.config import read_config
from utils.logger import load_logger

logging = load_logger(__name__)

config_list = read_config('config')



if __name__ == '__main__':
    print('Initializing diversity maximization algorithm...')

    # random.seed("7357")


    path = os.path.join('instances', 'Test_set', 'Test_set')

    for config in config_list:
        # execution.execute_instance(path, config)
        for n in range(config.get('experiments')):
            rng = random.Random(7357+n)
            execution.execute_directory(path, config, rng)

        os.remove(os.path.join('temp', 'execution.txt'))
