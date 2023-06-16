import itertools
import time

import folium
import osmnx as ox
import networkx as nx

ox.config(use_cache=True, log_console=True)


# Use OSMNx to find a possible route between origin and a destination
def find_route(origin, destination):
    try:
        origin_geo = ox.geocode(origin)
        destination_geo = ox.geocode(destination)
        graph = ox.graph_from_point(origin_geo, dist=2500, network_type='drive', simplify=False)

        orig = ox.nearest_nodes(graph, origin_geo[1], origin_geo[0])
        dest = ox.nearest_nodes(graph, destination_geo[1], destination_geo[0])
        route = nx.shortest_path(graph, orig, dest, 'length')
        total_distance = round(sum(ox.utils_graph.get_route_edge_attributes(graph, route, 'length')), 2)
        return route, total_distance, graph
    except:
        return 0, 0, 0


def calculate_full_route(origin, destinations):
    # Save algorithm starting time
    start_time = time.time()

    # Possible colors to use on the map (Currently using #b854ff which is purple)
    colors = ["#ffc629", "#2495ff", "#b854ff", "#ff47e3", "#ff213f", "#10a100"]

    # Get distance between origin to point and vice versa
    origin_to_point_dict, point_to_origin_dict = calculate_origin_to_point(origin, destinations)
    if origin_to_point_dict == 0 or point_to_origin_dict == 0:
        return 0, 0
    # Get distances between all points and each other
    point_a, point_b, two_point_distance = calculate_distance_between_two_points(destinations)
    # Get the shortest distance combination
    all_combo_routes, total_combo_distances, smallest_index = calculate_best_combos(destinations, point_a, point_b,
                                                                                    two_point_distance,
                                                                                    origin_to_point_dict,
                                                                                    point_to_origin_dict)

    total_distance = 0

    final_route = []
    final_graph = []

    geocodes = ox.geocode(origin)

    # Add origin to first point to distance and on the map
    path_nodes, distance, graph = find_route(origin, all_combo_routes[smallest_index][0])
    final_graph.append(graph)
    final_route.append(path_nodes)
    total_distance += distance
    route_map = ox.plot_route_folium(graph, path_nodes, color=colors[2])
    node = graph.nodes(data=True)[path_nodes[0]]
    # Put a marker on origin
    folium.Marker(location=[node['y'], node['x']], popup="Start", icon=folium.DivIcon(
        html=f"""<div style="font-family: courier new; color: blue; font-size: 50px; font-weight:bold">Start</div>""")).add_to(
        route_map)

    # Add all middle points to total distance and on the map
    for point in range(len(all_combo_routes[smallest_index]) - 1):
        path_nodes, distance, graph = find_route(all_combo_routes[smallest_index][point],
                                                 all_combo_routes[smallest_index][point + 1])
        final_graph.append(graph)
        final_route.append(path_nodes)
        route_map = ox.plot_route_folium(graph, path_nodes, color=colors[2], route_map=route_map)
        node = graph.nodes(data=True)[path_nodes[0]]
        folium.Marker(location=[node['y'], node['x']], popup=f"Point {point + 1}", icon=folium.DivIcon(
            html=f"""<div style="font-family: courier new; color: blue; font-size: 50px; font-weight:bold">{point + 1}</div>""")).add_to(
            route_map)
        total_distance += distance

    # Add last point to Origin distance to total distance and on the map.
    path_nodes, distance, graph = find_route(
        all_combo_routes[smallest_index][len(all_combo_routes[smallest_index]) - 1], origin)
    final_graph.append(graph)
    final_route.append(path_nodes)
    total_distance += distance
    route_map = ox.plot_route_folium(graph, path_nodes, color=colors[2], route_map=route_map)
    node = graph.nodes(data=True)[path_nodes[0]]
    folium.Marker(location=[node['y'], node['x']], popup=f"Point {len(all_combo_routes[smallest_index])}",
                  icon=folium.DivIcon(
                      html=f"""<div style="font-family: courier new; color: blue; font-size: 50px; font-weight:bold">{len(all_combo_routes[smallest_index])}</div>""")
                  ).add_to(route_map)

    # Prints to console for general information
    print(all_combo_routes[smallest_index])
    print(f"Actual shortest: {total_combo_distances[smallest_index]}")
    print(f"Total distance: {total_distance}")

    end_time = time.time()
    print(f"It took {end_time - start_time} total time to calculate the route.")
    # Only two digits after decimal point
    total_distance = "{:.2f}".format(total_distance)
    total_distance = (int(float((total_distance)))/1000)
    return route_map, total_distance


# Calculate distance between origin to each point and each point to origin
def calculate_origin_to_point(origin, destinations):
    origin_to_point_dict = {}
    origin_to_point = []
    origin_to_point_distance = []

    point_to_origin_dict = {}
    point_to_origin = []
    point_to_origin_distance = []

    for destination in destinations:
        path_nodes, distance, graph = find_route(origin, destination)
        if path_nodes == 0 or distance == 0 or graph == 0:
            return 0, 0
        origin_to_point.append(destination)
        origin_to_point_distance.append(distance)
        origin_to_point_dict[destination] = distance
        print(f"Calculated Origin to {destination} distance is {distance}")

        path_nodes, distance, graph = find_route(destination, origin)
        point_to_origin.append(destination)
        point_to_origin_distance.append(distance)
        point_to_origin_dict[destination] = distance
        print(f"Calculated {destination} to origin distance is {distance}")

    return origin_to_point_dict, point_to_origin_dict


# Calculate distance between two points, save in 3 lists and return
def calculate_distance_between_two_points(destinations):
    two_point_distance = []
    point_a = []
    point_b = []

    for destination in destinations:
        for sub_destination in destinations:
            if destination is not sub_destination:
                path_nodes, distance, graph = find_route(destination, sub_destination)
                point_a.append(destination)
                point_b.append(sub_destination)
                two_point_distance.append(distance)

    return point_a, point_b, two_point_distance


# Calculate best combinations
def calculate_best_combos(destinations, point_a, point_b, two_point_distance, origin_to_point_dict,
                          point_to_origin_dict):
    combinations = itertools.permutations(destinations)
    total_combo_distances = []
    all_combo_routes = []

    for combo in combinations:
        total_distance_of_combination = 0
        index = 0
        combo_list = []
        for x in range(len(combo) - 1):
            print(f"Calculating {combo[x]} to {combo[x + 1]}")
            total_distance_of_combination += get_distance(point_a, point_b, two_point_distance, combo[x], combo[x + 1])
            combo_list.append(combo[x])
        combo_list.append(combo[len(combo) - 1])
        total_combo_distances.append(total_distance_of_combination)
        all_combo_routes.append(combo_list)
        index += 1

    index = 0
    smallest = 99999999
    smallest_index = 0

    for combo in all_combo_routes:
        total_combo_distances[index] += origin_to_point_dict[combo[0]] + point_to_origin_dict[combo[len(combo) - 1]]
        if total_combo_distances[index] < smallest:
            smallest = total_combo_distances[index]
            smallest_index = index
        index += 1

    return all_combo_routes, total_combo_distances, smallest_index


# Get distance between two points from the already created lists
def get_distance(point_a, point_b, distances, from_a, to_b):
    index = 0
    for point in point_a:
        if point == from_a:
            if point_b[index] == to_b:
                return distances[index]
        index += 1
    return print("NO DISTANCE")
