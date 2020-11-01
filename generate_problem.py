import argparse
import time
import os
import json
import random
import numpy as np
from generate_map import *


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

    parser = argparse.ArgumentParser(description='script for generating truck and drone problem instances')

    parser.add_argument('-f', '--file', type=str, default='parameters/drive_and_fly_together_1x1.json',
                        help='Path to json parameters files')
    parser.add_argument('-o', '--output', type=str, default=f'problem_{curr_time}',
                        help='Path to output problem file')
    parser.add_argument("--show", type=str2bool, nargs='?',
                        const=True, default=False,
                        help="Show the generated problem environment")

    args = parser.parse_args()

    parameters_file = args.file
    problem_file = args.output

    head, tail = os.path.splitext(parameters_file)
    if tail != '.json':
        parameters_file = head + tail + '.json'

    head, tail = os.path.splitext(problem_file)
    if tail != '.pddl':
        problem_file = head + tail + '.pddl'

    problem_name, _ = os.path.splitext(problem_file)

    # load the parameters file
    with open(parameters_file, 'r') as fp:
        params = json.load(fp)

    # set the problem name in parameters
    params['general']['problem_name'] = problem_name

    # set the seed
    np.random.seed(params["general"]["seed"])
    random.seed(params["general"]["seed"])

    env = generate_map(params, show=args.show)
