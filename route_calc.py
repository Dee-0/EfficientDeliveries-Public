import itertools
import time

import folium
import osmnx as ox
import networkx as nx

ox.config(use_cache=True, log_console=True)

indexing = {}
full_route_nodes = []
full_route_distances = []


def find_route(origin,destination):

    origin_geo = ox.geocode(origin)
    destination_geo = ox.geocode(destination)
    graph = ox.graph_from_point(origin_geo, dist=2500, network_type='drive', simplify=False)

    orig = ox.nearest_nodes(graph, origin_geo[1], origin_geo[0])
    dest = ox.nearest_nodes(graph, destination_geo[1], destination_geo[0])
    route = nx.shortest_path(graph, orig, dest, 'length')
    total_distance = round(sum(ox.utils_graph.get_route_edge_attributes(graph, route, 'length')), 2)
    return route,total_distance,graph

def calculate_full_route(origin, destinations):

    start_time = time.time()
    lib_time = time.time()

    colors = ["#ffc629", "#2495ff", "#b854ff", "#ff47e3", "#ff213f", "#10a100"]

    combinations = itertools.permutations(destinations)

    total_combo_distances = []
    all_combo_routes = []

    two_point_distance = []
    point_a = []
    point_b = []

    origin_to_point_dict = {}
    origin_to_point = []
    origin_to_point_distance = []

    point_to_origin_dict = {}
    point_to_origin = []
    point_to_origin_distance = []

    for destination in destinations:
        path_nodes, distance, graph = find_route(origin, destination)
        origin_to_point.append(destination)
        origin_to_point_distance.append(distance)
        origin_to_point_dict[destination] = distance
        print(f"Calculated Origin to {destination} distance is {distance}")

        path_nodes, distance, graph = find_route(destination, origin)
        point_to_origin.append(destination)
        point_to_origin_distance.append(distance)
        point_to_origin_dict[destination] = distance
        print(f"Calculated {destination} to origin distance is {distance}")


    for destination in destinations:
        for sub_destination in destinations:
            if destination is not sub_destination:
                path_nodes, distance, graph = find_route(destination, sub_destination)
                point_a.append(destination)
                point_b.append(sub_destination)
                two_point_distance.append(distance)

    end_lib = time.time()
    for combo in combinations:
        total_distance_of_combination = 0
        index = 0
        combo_list = []
        for x in range(len(combo)-1):
            print(f"Calculating {combo[x]} to {combo[x+1]}")
            total_distance_of_combination += get_distance(point_a, point_b, two_point_distance, combo[x],combo[x+1])
            combo_list.append(combo[x])
        combo_list.append(combo[len(combo)-1])
        total_combo_distances.append(total_distance_of_combination)
        all_combo_routes.append(combo_list)
        index += 1

    index = 0
    smallest = 99999999
    smallest_index = 0

    for combo in all_combo_routes:
        total_combo_distances[index] += origin_to_point_dict[combo[0]] + point_to_origin_dict[combo[len(combo)-1]]
        if total_combo_distances[index] < smallest:
            smallest = total_combo_distances[index]
            smallest_index = index
        index += 1

    total_distance = 0

    final_route = []
    final_graph = []

    geocodes = ox.geocode(origin)

    full_route_nodes = []
    # Add origin to first point
    path_nodes, distance, graph = find_route(origin, all_combo_routes[smallest_index][0])
    final_graph.append(graph)
    final_route.append(path_nodes)
    total_distance += distance
    route_map = ox.plot_route_folium(graph, path_nodes, color=colors[2])
    node = graph.nodes(data=True)[path_nodes[0]]

    folium.Marker(location=[node['y'],node['x']], popup="Start",icon=folium.DivIcon(html=f"""<div style="font-family: courier new; color: blue; font-size: 50px; font-weight:bold">Start</div>""")).add_to(route_map)
    # Add all middle points
    for point in range(len(all_combo_routes[smallest_index])-1):
        path_nodes, distance, graph = find_route(all_combo_routes[smallest_index][point], all_combo_routes[smallest_index][point+1])
        final_graph.append(graph)
        final_route.append(path_nodes)
        route_map = ox.plot_route_folium(graph, path_nodes, color=colors[2], route_map=route_map)
        node = graph.nodes(data=True)[path_nodes[0]]
        folium.Marker(location=[node['y'],node['x']], popup=f"Point {point+1}",icon=folium.DivIcon(html=f"""<div style="font-family: courier new; color: blue; font-size: 50px; font-weight:bold">{point+1}</div>""")).add_to(route_map)
        total_distance += distance

    # Add last point to Origin
    path_nodes, distance, graph = find_route(all_combo_routes[smallest_index][len(all_combo_routes[smallest_index])-1], origin)
    final_graph.append(graph)
    final_route.append(path_nodes)
    total_distance += distance
    route_map = ox.plot_route_folium(graph, path_nodes, color=colors[2], route_map=route_map)
    node = graph.nodes(data=True)[path_nodes[0]]
    folium.Marker(location=[node['y'],node['x']], popup=f"Point {len(all_combo_routes[smallest_index])}",icon=folium.DivIcon(html=f"""<div style="font-family: courier new; color: blue; font-size: 50px; font-weight:bold">{len(all_combo_routes[smallest_index])}</div>""")
   ).add_to(route_map)

    print(all_combo_routes[smallest_index])
    print(f"Actual shortest: {total_combo_distances[smallest_index]}")
    print(f"Total distance: {total_distance}")

    end_time = time.time()
    print(f"It took {end_time-start_time} total time to calculate the route.")
    #print(f"It took {end_lib - lib_time} for the library alone.")
    return route_map,total_distance

def get_distance(point_a,point_b,distances, from_a,to_b):
    index = 0
    for point in point_a:
        if point == from_a:
            if point_b[index] == to_b:
                return distances[index]
        index += 1
    return print("NO DISTANCE")

