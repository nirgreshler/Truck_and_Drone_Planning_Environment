import argparse
import time
import os
import json
import random
import numpy as np
from generate_map import *
from utils.general_functions import *
from utils.graphs import *


def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


if __name__ == "__main__":
    curr_time = time.strftime('%d_%m_%H_%M_%S')

    # parse input arguments
    parser = argparse.ArgumentParser(description='script for generating truck and drone problem instances')

    parser.add_argument('-f', '--file', type=str, default='parameters/drive_and_fly_together_1x1.json',
                        help='Path to json parameters files')
    parser.add_argument('-o', '--output', type=str, default=f'problem_{curr_time}',
                        help='Path to output problem file')
    parser.add_argument("--show", type=str2bool, nargs='?',
                        const=True, default=False,
                        help="Show the generated problem environment")
    args = parser.parse_args()

    # get the input and output files
    parameters_file = get_file(args.file, 'json')
    problem_file = get_file(args.output, 'pddl')
    problem_name, _ = os.path.splitext(problem_file)

    # load the parameters file
    with open(parameters_file, 'r') as fp:
        params = json.load(fp)

    # set the problem name in parameters
    params['general']['problem_name'] = problem_name

    # set the seed
    np.random.seed(params["general"]["seed"])
    random.seed(params["general"]["seed"])

    # generate the environment
    env = generate_map(params, show=args.show)

    # construct adjacency matrix for the truck nodes
    truck_adj_max = np.ones(env["truck_dist_matrix"].shape)
    truck_adj_max[env["truck_dist_matrix"] != np.inf] = 0

    # set the truck initial position as the first truck node, and the goal position as the last truck node
    truck_start = env["truck_nodes"][0]
    truck_goal = env["truck_nodes"][-1]

    # build the truck graph
    g_truck = construct_truck_graph(env, params)
    # build the drone graph
    g_drone, rrt_list = construct_drone_graph(env, params,
                                              one_package=params["general"][
                                                              "domain_name"] != 'drive_and_fly_together_multiple')

    # construct the PDDL
    os.getcwd()
    local_problem_file = write_pddl(g_truck=g_truck, g_drone=g_drone,
                                    truck_start=truck_start, truck_goal=truck_goal, params=params)
