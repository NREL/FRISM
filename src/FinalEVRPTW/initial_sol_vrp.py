import random
import matplotlib.pyplot as plt
import numpy as np
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import math
import time
from data_model import create_data_model




def solve_initial_vrp(data,num_customers=None):

    if num_customers is None:
        num_customers = len(data['customer_nodes'])
        
    """Solves the initial VRP without considering charging stations.""" 
    # Only include the depot and customer nodes (exclude charging stations)
    num_nodes = len(data['customer_nodes']) + 1  # Depot + customers only
    
    # Create the routing index manager for depot and customer nodes
    manager = pywrapcp.RoutingIndexManager(num_nodes, data['num_vehicles'], data['depot'])
    
    # # Verify node mapping between internal index and actual data nodes
    # print("Verifying node mapping:")
    # for i in range(num_nodes):
    #     actual_node = data['depot'] if i == 0 else data['customer_nodes'][i - 1]
    #     print(f"Internal index {i} maps to actual node {actual_node} in the data model")

    # Create Routing Model
    routing = pywrapcp.RoutingModel(manager)

    # Create and register transit callback (travel time)
    def time_callback(from_index, to_index):
        """Returns the travel time between two nodes."""
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        travel_time = data['distance_matrix'][from_node][to_node]
        # Service time at the 'from_node'
        service_time = data['service_times'][from_node]
        return travel_time + service_time

    transit_callback_index = routing.RegisterTransitCallback(time_callback)

    # Set cost evaluator
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Time Dimension
    routing.AddDimension(
        transit_callback_index,
        0,  # No slack
        10000,  # Maximum time per vehicle
        False,  # Don't force Start cumul to zero
        'Time'
    )

    time_dimension = routing.GetDimensionOrDie('Time')

    # Add time window constraints (for depot and customer nodes only)
    for location_idx, time_window in enumerate(data['time_windows'][:num_nodes]):
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])

    # Add capacity constraint for customers only
    def demand_callback(from_index):
        """Returns the demand at each node."""
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # Null slack
        data['vehicle_capacities'],
        True,
        'Capacity'
    )

    # Set fixed vehicle cost
    vehicle_cost = 1000
    for vehicle_id in range(data['num_vehicles']):
        routing.SetFixedCostOfVehicle(vehicle_cost, vehicle_id)

    # Search parameters
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.seconds = 18 * num_customers

    # Record the start time before solving 
    start_time = time.time()
    # Solve the problem
    solution = routing.SolveWithParameters(search_parameters)
    # Record the end time after solving
    end_time = time.time()

    if solution:
        print("Initial VRP solution found.")
        return manager, routing, solution
    else:
        print("No solution found for the initial VRP.")
        return None, None, None

    # Calculate the time taken to solve
    time_taken = end_time - start_time
    print(f"Time taken to solve VRP only problem: {time_taken:.2f} seconds")





# # Test the code:
# def main():
#     print("Starting the VRP solution with Google OR Tools...")

#     data = create_data_model(10, 3)

#     manager, routing, solution = solve_initial_vrp(data)
#     if solution:
#         # Extract only the routes that serve customers
#         routes_with_customers = get_routes_with_customers(manager, routing, solution, data)
#         print("Routes with customers:")
#         print(routes_with_customers)
#         print("arrival times of nodes:")
#         extract_arrival_times(data,manager,routing, solution)
#         plot_solution(data,manager,routing,solution)

#     else:
#         print("No initial solution found for VRP.")


# if __name__ == '__main__':
#     main()