import numpy as np
import pickle
import os
from pathlib import Path
from utils.general_functions import *
from rrt.src.search_space.search_space import SearchSpace
from rrt.src.utilities.obstacle_generation import *
from rrt.src.utilities.plotting import Plot


def generate_map(params=None, show=True):
    p = params['env_struct']
    if p is None:
        # Parameters:
        block_size_x, block_size_y = 100, 100
        num_obstacles_in_block = 20
        num_drone_points_in_block = 3
        map_name = "rrt_star_2d_with_random_obstacles"
        num_blocks_x = 3
        num_blocks_y = 3
    else:
        block_size_x, block_size_y = p["block_size_x"], p["block_size_y"]
        num_obstacles_in_block = p["num_obstacles_in_block"]
        num_drone_points_in_block = p["num_drone_points_in_block"]
        map_name = p["map_name"]
        num_blocks_x = p["num_blocks_x"]
        num_blocks_y = p["num_blocks_y"]

    all_corners = []
    all_obstacles = []
    all_drone_checkpoints = []

    X = SearchSpace(np.array([(0, block_size_x * num_blocks_x),
                              (0, block_size_y * num_blocks_y)]))

    for block_x in range(num_blocks_x):
        for block_y in range(num_blocks_y):
            corners = [[block_size_x * block_x, block_size_y * block_y],
                       [block_size_x * (block_x + 1) , block_size_y * block_y],
                       [block_size_x * block_x, block_size_y * (block_y + 1)],
                       [block_size_x * (block_x + 1), block_size_y * (block_y + 1)]]
            all_corners += corners
            X_dimensions = np.array([(block_size_x * block_x, block_size_x * (block_x + 1)),
                                     (block_size_y * block_y, block_size_y * (block_y + 1))])  # dimensions of Search Space

            # Generate truck
            drone_checkpoints = np.random.uniform(low=(block_size_x * block_x, block_size_y * block_y),
                                                  high=(block_size_x * (block_x + 1), block_size_y * (block_y + 1)),
                                                  size=(num_drone_points_in_block, 2))
            all_drone_checkpoints.append(drone_checkpoints)
            # create Search Space
            search_space = SearchSpace(X_dimensions)
            Obstacles = generate_random_obstaclesV2(search_space, X, corners, num_obstacles_in_block, drone_checkpoints)
            all_obstacles += Obstacles

    all_drone_checkpoints = np.vstack(all_drone_checkpoints)

    all_corners = np.unique(all_corners, axis=0)
    distance_matrix = generate_distance_matrix(all_corners, TH=block_size_x + 1e-3)

    if show:
        # # plot
        plot = Plot(map_name, plot_size=1000)
        plot.plot_obstacles(search_space, all_obstacles)
        for corner in all_corners:
            plot.plot_start(search_space, corner)
        plot.plot_nodes(search_space, all_drone_checkpoints, color='red', size=20)
        plot.plot_nodes(search_space, all_corners, color='blue', size=50)
        plot.draw(auto_open=True)

    env = {
        "search_space": X,
        "drone_checkpoints": np.array(all_drone_checkpoints, dtype='int'),
        "truck_nodes": all_corners,
        "obstacles": all_obstacles,
        "truck_dist_matrix": distance_matrix
    }
    return env

def save_env(env, curr_time):
    # with open(f'files/environments/ {curr_time}.pkl', 'wb') as f:
    #     pickle.dump(env, f, pickle.HIGHEST_PROTOCOL)
    np.save(f'files/environments/{curr_time}', env)


