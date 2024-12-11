# Import necessary modules for the test
import random
import numpy as np
import math
import contextlib
import os

from ortools.constraint_solver import routing_enums_pb2, pywrapcp

# Check if the 'results' folder exists, if not, create it
if not os.path.exists('results'):
    os.makedirs('results')
# Check if the 'data' folder exists, if not, create it
if not os.path.exists('data'):
    os.makedirs('data')

# Define the generate_unique_location function
def generate_unique_location(existing_locations, range_min=-50, range_max=50):
    while True:
        x = random.randint(range_min, range_max)
        y = random.randint(range_min, range_max)
        if (x, y) not in existing_locations:
            return (x, y)

# Create the data model
def create_data_model(num_customers, num_stations):
    data = {}
    locations = [(0, 0)]  # Depot at (0,0)

    for _ in range(num_customers):
        locations.append(generate_unique_location(locations))
    for _ in range(num_stations):
        locations.append(generate_unique_location(locations))

    data['locations'] = locations

    def euclidean_distance(loc1, loc2):
        return round(math.hypot(loc1[0] - loc2[0], loc1[1] - loc2[1]))

    distance_matrix = []
    for i in range(len(locations)):
        row = []
        for j in range(len(locations)):
            if i == j:
                row.append(0)
            else:
                row.append(euclidean_distance(locations[i], locations[j]))
        distance_matrix.append(row)

    data['distance_matrix'] = distance_matrix

    num_vehicles = math.ceil(0.4 * num_customers)
    data['num_vehicles'] = num_vehicles

    # Specify vehicle types and factors
    # Split vehicles into EVs and ICEs (50% each)
    ev_count = num_vehicles // 2
    ice_count = num_vehicles - ev_count  # Remaining vehicles are ICEs to handle odd cases
    data['vehicle_types'] = [ev_count, ice_count]  # [EV count, ICE count]
    data['vehicle_factors'] = {'EV': 1, 'ICE': 10}  # EV: 1x service time, ICE: 10x service time
    data['vehicle_type_list'] = ['EV'] * ev_count + ['ICE'] * ice_count

    # Assign uniform capacities based on vehicle type
    type_capacities = {'EV': 25, 'ICE': 25}  # Example: EVs have capacity 25, ICEVs have capacity 25
    data['vehicle_capacities'] = [type_capacities[vt] for vt in data['vehicle_type_list']]

    data['depot'] = 0
    data['customer_nodes'] = list(range(1, num_customers + 1))
    data['charging_stations'] = list(range(num_customers + 1, num_customers + 1 + num_stations))
    data['demands'] = [0] + [random.randint(1, 10) for _ in range(num_customers)] + [0] * num_stations
    data['service_times'] = [0] + [random.randint(2, 5) for _ in range(num_customers)] + [0] * num_stations
    # Assign battery capacities only for EVs
    data['battery_capacities'] = [
        100 if vehicle_type == 'EV' else None for vehicle_type in data['vehicle_type_list']]
    data['time_windows'] = [(0, 1000)] + [(random.randint(0, 50), 500) for _ in range(num_customers)] + [(0, 1000)] * num_stations
    data['charging_rate'] = 1

    # Redirect print output to a file
    output_file=f'data/data_model_{num_customers}_{num_stations}.txt'
    with open(output_file, "w") as f:
        with contextlib.redirect_stdout(f):
            print("Location coordinates of network setup:")
            print(data['locations'])
            print(f"\nDepot Index: {data['depot']}")
            print(f"\nCustomer node indices: {data['customer_nodes']}")
            print(f"\nCharging station indices: {data['charging_stations']}")
            print(f"\nRandom service times: {data['service_times']}")
            print(f"\nTime Windows: {data['time_windows']}")
            print(f"\nDemands: {data['demands']}")
            print("Vehicle type list:", data['vehicle_type_list'])
            print("Vehicle capacities:", data['vehicle_capacities'])
            print(f"\nBattery Capacities: {data['battery_capacities']}")
            print("\nDistance Matrix:")
            for row in data['distance_matrix']:
                print(row)
    
    

    return data

# Solve the VRP problem
def solve_initial_vrp(data,num_customers=None):

    if num_customers is None:
        num_customers = len(data['customer_nodes'])
    num_nodes = len(data['customer_nodes']) + 1
    manager = pywrapcp.RoutingIndexManager(num_nodes, data['num_vehicles'], data['depot'])
    routing = pywrapcp.RoutingModel(manager)

    def time_callback(from_index, to_index):
        """Returns the travel time between two nodes, adjusted for vehicle type."""
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        travel_time = data['distance_matrix'][from_node][to_node]
        
        # Get the vehicle type, default to EV if not bound
        vehicle_id = routing.VehicleVar(from_index)
        if solution is not None:  # Ensure the variable is resolved only when solving
            vehicle_type = data['vehicle_type_list'][solution.Value(vehicle_id)]
        else:
            vehicle_type = 'EV'  # Default to EV (or handle based on your preference)

        # Adjust service time based on vehicle type
        service_time = data['service_times'][from_node] * data['vehicle_factors'][vehicle_type]
        return travel_time + service_time


    transit_callback_index = routing.RegisterTransitCallback(time_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    routing.AddDimension(
        transit_callback_index,
        0,
        10000,
        False,
        'Time'
    )

    time_dimension = routing.GetDimensionOrDie('Time')

    for location_idx, time_window in enumerate(data['time_windows'][:num_nodes]):
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])

    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,
        data['vehicle_capacities'],
        True,
        'Capacity' 
    )

    # Define fixed costs for vehicle types
    fixed_costs = {'EV': 800, 'ICE': 1000}  # Example: EVs cost 800, ICEs cost 1000
    # Assign fixed costs to each vehicle based on its type
    for vehicle_id in range(data['num_vehicles']):
        vehicle_type = data['vehicle_type_list'][vehicle_id]
        vehicle_cost = fixed_costs[vehicle_type]  # Get the cost based on vehicle type
        routing.SetFixedCostOfVehicle(vehicle_cost, vehicle_id)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.seconds = 15 * num_customers

    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        return manager, routing, solution
    else:
        return None, None, None

# # Generate data and solve for 10 customers 5 charging stations
# data = create_data_model(10, 5)
# manager, routing, solution = solve_initial_vrp(data)

# if solution:
#     # Extract and display solution details
#     results = []
#     for vehicle_id in range(data['num_vehicles']):
#         index = routing.Start(vehicle_id)
#         route = []
#         while not routing.IsEnd(index):
#             route.append(manager.IndexToNode(index))
#             index = solution.Value(routing.NextVar(index))
#         route.append(manager.IndexToNode(index))
        
#         # Get the vehicle type ('EV' or 'ICE') based on the vehicle_id
#         vehicle_type = data['vehicle_type_list'][vehicle_id]
#         results.append((vehicle_type, route))  # Append vehicle type and route

#     print(results)
# else:
#     print("No solution found.")
