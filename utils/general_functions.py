import numpy as np
import os
from rrt.src.utilities.plotting import Plot
import json
from pathlib import Path
import time


def get_file(filepath, ext):
    head, tail = os.path.splitext(filepath)
    if tail != '.json':
        filepath = head + tail + '.'
    return filepath


def save_params(params, curr_time):
    with open(f'files/parameters/{curr_time}.json', 'w') as fp:
        json.dump(params, fp, indent=4)


def load_params(params_mode='last'):
    if params_mode == "last":
        path = sorted(Path('files/parameters/').iterdir(), key=os.path.getmtime)[-1].__str__()
    else:
        path = f'files/parameters/{params_mode}'
    with open(path, 'r') as fp:
        params = json.load(fp)
    return params


def generate_distance_matrix(all_corners, TH=None):
    num_corners = all_corners.shape[0]
    D_M = np.zeros((num_corners, num_corners))
    for i, corner in enumerate(all_corners):
        D_M[:, i] =  ((corner - all_corners) ** 2).sum(axis=1) ** 0.5
    if TH is not None:
        D_M[D_M >= TH] = np.inf
    return D_M


def calc_path_length(path):
    dist = 0
    n_points = len(path)
    for pi in range(1, n_points):
        dist += np.linalg.norm(np.array(path[pi]) - np.array(path[pi - 1]))
    return dist


def plot_solution(env, truck_route, drone_route, plot_title='Truck & Drone Routes'):
    search_space, obstacles = env["search_space"], env["obstacles"]
    plot = Plot("", plot_size=1000, title=plot_title)
    plot.plot_obstacles(search_space, obstacles)
    # for corner in all_corners:
    #     plot.plot_start(search_space, corner)
    # plot.plot_nodes(search_space, all_drone_checkpoints, color='red', size=20)
    # plot.plot_nodes(search_space, all_corners, color='blue', size=50)
    plot.plot_nodes(search_space, truck_route.values(), color='blue', size=50)
    truck_time_keys = list(truck_route.keys())
    for tki in range(len(truck_time_keys) - 1):
        path = [truck_route[truck_time_keys[tki]], truck_route[truck_time_keys[tki+1]]]
        plot.plot_path(search_space, path, "blue")

    drone_paths = list(drone_route.values())
    plot.plot_nodes(search_space, [d[-1] for d in drone_paths], color='red', size=50)
    for dp in drone_paths:
        plot.plot_path(search_space, dp)

    plot.draw(auto_open=True)
    time.sleep(0.1)


def parse_solution(solution_dir, rrt_list, iter_=None):
    if iter_ is None:
        files = [f for f in os.listdir(f'{solution_dir}') if "PLAN" in f]
        iter_ = len(files)
    problem_name = solution_dir.split("/")[-1]
    with open(f'{solution_dir}/{problem_name}_PLAN.txt.{iter_}', newline='\n') as f:
        c = f.readlines()
    truck_route = {}
    drone_route = {}
    opt_segments = []
    last_truck_line = []

    all_from = [r[0] for r in rrt_list]
    all_to = [r[-1] for r in rrt_list]

    for li, line in enumerate(c):
        if 'truck-drive-alone' in line and li < len(c)-1:
            # get the delivery point
            loc_deliver_to = c[li-1].split(' ')[3][:-1].split('_')[1:]
            if not 'truck-drive-alone' in c[li+1] and 'drone-deliver' in c[li-1]:
                loc_from = line.split(' ')[2].split('_')[1:]
                loc_to = line.split(' ')[3][:-1].split('_')[1:]
                loc_from = (float(loc_from[0]), float(loc_from[1]))
                loc_to = (float(loc_to[0]), float(loc_to[1]))
                loc_deliver_to = (float(loc_deliver_to[0]), float(loc_deliver_to[1]))
                opt_segments.append([loc_from, loc_to, loc_deliver_to, li])

        if 'truck-drive' in line:
            last_truck_line = line
            time = float(line.split(':')[0])
            tloc = line.split(' ')[2].split('_')[1:]
            truck_route[time] = (float(tloc[0]), float(tloc[1]))
        elif 'drone-deliver' in line or 'drone-return' in line or 'drone-deliver-out' in line:
            time = float(line.split(':')[0])
            loc_from = line.split(' ')[2].split('_')[1:]
            loc_to = line.split(' ')[3][:-1].split('_')[1:]
            loc_from = (float(loc_from[0]), float(loc_from[1]))
            loc_to = (float(loc_to[0]), float(loc_to[1]))
            # find the corresponding RRT route
            drone_route[time] = [rrt_list[i] for i, l in
                                 enumerate(zip(all_from, all_to)) if
                                 (loc_from == l[0] and loc_to == l[1]) or
                                 (loc_from == l[1] and loc_to == l[0])][0]

    # add the destination of the last truck drive
    time_start = float(last_truck_line.split(':')[0])
    time_taken = float(last_truck_line.split('[')[-1].split(']')[0])
    time = time_start + time_taken
    tloc = last_truck_line.split(' ')[3][:-1].split('_')[1:]
    truck_route[time] = (float(tloc[0]), float(tloc[1]))

    return truck_route, drone_route, opt_segments, c, float(c[0].split(' ')[-1][0:-1])