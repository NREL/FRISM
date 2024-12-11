import random
import matplotlib.pyplot as plt
import numpy as np
import math
import time
import re

from hetero_ini_vrp import create_data_model,solve_initial_vrp
from insert_ch_stn import insert_charging_stations,insert_charging_stations_single_route,find_accessible_charging_station
from VNS import variable_neighborhood_search
from print_plot import print_solution_routes, plot_solution_routes




def main():
    print("----------------------------------------------------")
    print("Starting the VRP script ...")

    # Step 1: Create data model
    num_customers = 100
    num_stations = int(num_customers * 0.5)

    data = create_data_model(num_customers, num_stations)

    # Step 2: Solve the initial VRP without considering charging stations
    manager, routing, solution = solve_initial_vrp(data, num_customers=num_customers)
    if solution is None:
        print("No solution found for the initial VRP.")
        return

    # Step 3: Separate ICE and EV routes
    ev_routes = []
    ice_routes = []

    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        route = []
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route.append(node_index)
            index = solution.Value(routing.NextVar(index))
        route.append(data['depot'])  # Return to depot

        # Separate based on vehicle type
        customer_nodes_in_route = [node for node in route if node in data['customer_nodes']]
        if customer_nodes_in_route:
            vehicle_type = data['vehicle_type_list'][vehicle_id]
            if vehicle_type == 'EV':
                ev_routes.append(route)
            elif vehicle_type == 'ICE':
                ice_routes.append(route)

    print("EV Routes:", ev_routes)
    print("ICE Routes:", ice_routes)

    # Step 4: Gather customers served by ICE routes
    served_by_ice = set(node for route in ice_routes for node in route if node in data['customer_nodes'])
    remaining_customers = set(data['customer_nodes']) - served_by_ice

    print("Customers served by ICE routes:", served_by_ice)
    print("Remaining customers to be processed for EV:", remaining_customers)

    # Step 5: Process EV routes for charging station insertion
    updated_ev_routes, unvisited_customers = insert_charging_stations(data, ev_routes, remaining_customers)
    print("\nFeasible EV Routes after Charging Station Insertion:")
    for route in updated_ev_routes:
        print(route)

    # Handle unvisited customers for EV
    if unvisited_customers:
        print(f"Unvisited customers after EV adjustment: {unvisited_customers}")
        # return  # Stop if not all customers are served

        # Add unvisited customers back to remaining_customers
        remaining_customers.update(unvisited_customers)

    # Step 6: Optimize EV routes using VNS
    print("Starting VNS optimization for EV routes...")
    optimized_ev_routes = variable_neighborhood_search(data, updated_ev_routes, num_customers=num_customers, remaining_customers=remaining_customers)
    print("\nOptimized EV Routes (after VNS):")
    for route in optimized_ev_routes:
        print(route)

    # Step 7: Combine ICE and EV routes
    print("\nFinal ICE Routes:")
    for route in ice_routes:
        print(route)

    print("\nFinal EV Routes (Optimized):")
    for route in optimized_ev_routes:
        print(route)

    # Filter out depot-only routes like [0, 0]
    filtered_ice_routes = [route for route in ice_routes if len(route) > 2 or (len(route) == 2 and route[0] != route[1])]
    filtered_ev_routes = [route for route in optimized_ev_routes if len(route) > 2 or (len(route) == 2 and route[0] != route[1])]

    # Combine ICE and EV routes after filtering
    final_routes = filtered_ice_routes + filtered_ev_routes

    print("\nFinal Combined Heterogeneous Routes (ICE + Optimized EV):")
    for route in final_routes:
        print(route)

    # Save the final solution
    output_print_file = f'results/final_heterogeneous_routes_{num_customers}_{num_stations}.txt'
    with open(output_print_file, 'w') as f:
        f.write("Final ICE Routes:\n")
        for route in filtered_ice_routes:
            f.write(" -> ".join(map(str, route)) + "\n")

        f.write("\nFinal EV Routes (Optimized):\n")
        for route in filtered_ev_routes:
            f.write(" -> ".join(map(str, route)) + "\n")

        f.write("\nFinal Combined Heterogeneous Routes (ICE + Optimized EV):\n")
        for route in final_routes:
            f.write(" -> ".join(map(str, route)) + "\n")

    print(f"Final solution saved to {output_print_file}")


    # Assume `ice_routes` and `optimized_ev_routes` are already computed
    output_plot_file = f'results/heterogeneous_routes_{num_customers}_{num_stations}.png'
    plot_solution_routes(
        data,
        ice_routes=ice_routes,
        ev_routes=optimized_ev_routes,
        filename=output_plot_file
    )
     




if __name__ == '__main__':
    main()
