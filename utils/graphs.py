from utils.Graph import Graph
from utils.general_functions import *
from algorithmic.motion_planning import plan_rrt_star


def construct_truck_graph(env, params):
    truck_dist_matrix = env["truck_dist_matrix"]
    truck_nodes = env["truck_nodes"]
    g_truck = Graph()
    for i in range(truck_dist_matrix.shape[0]):
        edge_list = {tuple(truck_nodes[ni]): np.round(dist / params["truck_settings"]['vel'], 2) for ni, dist in
                     enumerate(truck_dist_matrix[i]) if dist != np.inf and ni != i}
        g_truck.add_vertex(tuple(truck_nodes[i]), edge_list)
    return g_truck


def construct_drone_graph(env, params, one_package=True):
    drone_checkpoints, truck_nodes = env["drone_checkpoints"], env["truck_nodes"]
    g_drone = Graph()

    battery_time = params["drone_settings"]["full_battery_time"]
    drone_vel = params["drone_settings"]["vel"]

    rrt_list = []

    if one_package:
        nodes = truck_nodes
    else:
        nodes = np.concatenate([truck_nodes, drone_checkpoints])

    for pi, p in enumerate(drone_checkpoints):
        print(f'Calculating RRT: {pi+1}/{len(drone_checkpoints)}')
        dists = np.round(np.linalg.norm(nodes - p, axis=1), 2)
        times = dists / drone_vel
        reachable_nodes_idx = (0 < times) & (times < battery_time)
        reachable_nodes = nodes[reachable_nodes_idx]
        edge_list = {}
        for node in reachable_nodes:
            drone_path = plan_rrt_star(env["search_space"], env["obstacles"],
                                       tuple(node), tuple(p), show=False)

            if drone_path is None:
                continue
            # Add RRT path to list
            rrt_list.append(drone_path)
            dist = calc_path_length(drone_path)
            time_to_travel = np.round(dist / drone_vel, 2)
            if time_to_travel < battery_time:
                edge_list[tuple(node)] = time_to_travel

        if len(edge_list):
            g_drone.add_vertex(tuple(np.array(p, dtype='int')), edge_list)

    # drone_flight_range = params["env_struct"]["drone_flight_range"]
    # for pi, p in enumerate(drone_checkpoints):
    #     print(f'Calculating RRT: {pi+1}/{len(drone_checkpoints)}')
    #     if params["env_struct"]["rrt_flight_range"]:
    #         edge_list = {}
    #         dists = np.round(np.linalg.norm(truck_nodes - p, axis=1), 2)
    #         reachable_truck_nodes_idx = dists < drone_flight_range
    #         reachable_truck_nodes = truck_nodes[reachable_truck_nodes_idx]
    #         for node in reachable_truck_nodes:
    #             drone_path = plan_rrt_star(env["search_space"], env["obstacles"],
    #                                        tuple(node), tuple(p), show=False)
    #             if drone_path is None:
    #                 continue
    #             dist = calc_path_length(drone_path)
    #             if dist < drone_flight_range:
    #                 time_to_travel = dist / params["drone_vel"]
    #                 edge_list[tuple(node)] = time_to_travel
    #     else:
    #         dists = np.round(np.linalg.norm(truck_nodes - p, axis=1), 2)
    #         reachable_truck_nodes_idx = dists < drone_flight_range
    #         reachable_truck_nodes = truck_nodes[reachable_truck_nodes_idx]
    #         reachable_truck_nodes_dists = dists[reachable_truck_nodes_idx]
    #         edge_list = {tuple(n): np.round(reachable_truck_nodes_dists[ni] / params["drone_vel"], 2) for ni, n in enumerate(reachable_truck_nodes)}
    #
    #     if len(edge_list):
    #         g_drone.add_vertex(tuple(np.array(p, dtype='int')), edge_list)

    return g_drone, rrt_list