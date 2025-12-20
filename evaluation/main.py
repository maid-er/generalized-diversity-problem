'''Main function to execute instance solution set evaluation'''
import random

import utils


'''Variables defined by the user'''
SET = 'Test_set'
SUBSET = 'Test_set'
PLOT_PARETO_FRONTS = True


'''Main evaluation function'''
if __name__ == '__main__':

    random.seed(42)

    # Directory with results
    result_dir = 'output_all_experiments'

    # Plot Pareto Fronts of all the analyzed algorithms and instances
    common_inst = utils.get_coincident_instances(result_dir, SET, SUBSET)
    if PLOT_PARETO_FRONTS:
        utils.plot_pareto_fronts(result_dir, SET, SUBSET, common_inst)

    utils.calculate_performance_indicators(result_dir, SET, SUBSET, common_inst)
