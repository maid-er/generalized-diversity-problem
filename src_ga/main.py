'''Main function'''
import os

from utils import execution
from utils.logger import load_logger

logging = load_logger(__name__)


if __name__ == '__main__':
    logging.info('Initializing diversity maximization with NSGA-II algorithm...')

    path = os.path.join('instances', 'GDP', 'GKD-b_n50')

    for n in range(1):
        execution.execute_directory(path)

    os.remove(os.path.join('temp', 'execution.txt'))
