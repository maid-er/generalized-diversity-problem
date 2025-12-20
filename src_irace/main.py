'''Main function'''
import argparse
import os
import random
random.seed(7357)

from utils import execution
from utils.config import read_config
from utils.logger import load_logger

logging = load_logger(__name__)

config_list = read_config('config')



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--std_interval", type=float, required=True)
    parser.add_argument("--threshold", type=float, required=True)
    parser.add_argument("--beta", type=str, required=True)
    parser.add_argument("--seed", type=int, required=True)

    args = parser.parse_args()
    print('Initializing diversity maximization algorithm...')
    rng = random.Random(7357)
    config = config_list[0]
    print(config)
    config['parameters']['std_multiplier'] = float(args.std_interval)
    config['parameters']['threshold'] = float(args.threshold)
    config['parameters']['beta'] = float(args.beta)
    print(config)
    path = os.path.join('instances', 'Test_set', 'Test_set', args.instance)

    hv = execution.execute_instance(path, config)
    print(hv)
    rng = random.Random(int(args.seed))
    # execution.execute_directory(path, config, rng)

    os.remove(os.path.join('temp', 'execution.txt'))

if __name__ == "__main__":
    main()
