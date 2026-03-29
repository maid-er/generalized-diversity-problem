'''Main function'''
import argparse
import os
import random
random.seed(7357)

from utils import execution
from utils.config import read_config
from utils.logger import load_logger
from utils.results import OutputHandler

logging = load_logger(__name__)

config_list = read_config('config')



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--instance", type=str, help="Path to the instance file")
    parser.add_argument("--std_interval", type=float, required=True)
    parser.add_argument("--threshold", type=float, required=True)
    parser.add_argument("--beta", type=float, required=True)
    parser.add_argument("--delta", type=float, required=True)
    parser.add_argument("--seed", type=int, required=True)

    args = parser.parse_args()
    # print('Initializing diversity maximization algorithm...')
    rng = random.Random(args.seed)
    config = config_list[0]
    # print(config)
    config['parameters']['std_multiplier'] = float(args.std_interval)
    config['parameters']['threshold'] = float(args.threshold)
    config['parameters']['beta'] = float(args.beta)
    config['parameters']['delta'] = float(args.delta)
    # print(config)
    path = os.path.join('instances', 'Test_set', 'Test_set', args.instance)
    results = OutputHandler()
    hv = execution.execute_instance(path, config, results, rng, args.seed)
    print(-hv)
    # execution.execute_directory(path, config, rng)

    # os.remove(os.path.join('temp', 'execution.txt'))

if __name__ == "__main__":
    main()
