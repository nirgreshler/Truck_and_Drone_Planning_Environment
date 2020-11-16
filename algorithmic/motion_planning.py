from rrt.src.rrt.rrt_star import RRTStar
from rrt.src.search_space.search_space import SearchSpace
from rrt.src.utilities.obstacle_generation import generate_random_obstacles
from rrt.src.utilities.plotting import Plot

import numpy as np


def plan_rrt_star(search_space, obstacles, start_config, goal_config, show=True, fine=False):
    # X_dimensions = np.array([(0, 100), (0, 100)])  # dimensions of Search Space

    if fine:
        Q = np.array([(2, 1)])  # length of tree edges
        max_samples = 3000  # max number of samples to take before timing out
        rewire_count = 128  # optional, number of nearby branches to rewire
    else:
        Q = np.array([(8, 4)])  # length of tree edges
        max_samples = 1000  # 1024  # max number of samples to take before timing out
        rewire_count = 32  # 128  # optional, number of nearby branches to rewire
    r = 1  # length of smallest edge to check for intersection with obstacles
    prc = 0.1  # probability of checking for a connection to goal

    # Generate truck destinations
    # truck_dst = np.random.randint(0, 100, (10, 2))

    # # create Search Space
    # X = SearchSpace(X_dimensions)
    # n = 50
    # Obstacles = generate_random_obstacles(X, start_config, goal_config, n, truck_dst)
    # create rrt_search
    rrt = RRTStar(search_space, Q, start_config, goal_config, max_samples, r, prc, rewire_count)
    path = rrt.rrt_star()

    if show:
        # plot
        plot = Plot("rrt_star_2d_with_random_obstacles")
        plot.plot_tree(search_space, rrt.trees)
        if path is not None:
            plot.plot_path(search_space, path)
        plot.plot_obstacles(search_space, obstacles)
        plot.plot_start(search_space, start_config)
        plot.plot_goal(search_space, goal_config)
        plot.draw(auto_open=True)

    return path