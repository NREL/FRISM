import random
import matplotlib.pyplot as plt
import numpy as np
import math
import time
import re

from data_model import create_data_model
from initial_sol_vrp import solve_initial_vrp
from new_insert_ch_stn import insert_charging_stations,insert_charging_stations_single_route,find_accessible_charging_station
from new_VNS_chat import variable_neighborhood_search, intra_route_2opt_swap, intra_route_or_opt,inter_route_swap, inter_route_relocate, route_merge, local_search, intra_route_2opt_swap_single_route
from print_plot import print_solution_routes, plot_solution_routes







def main():
    print("----------------------------------------------------")
    print("Starting the VRP script ...")

    # Step 1: Create data model
    num_customers = 10
    num_stations = int(num_customers * 0.5)   # replace with actual number of charging stations

    data = create_data_model(num_customers, num_stations)
    
    # Step 2: Solve the initial VRP without considering charging stations
    manager, routing, solution = solve_initial_vrp(data,num_customers=num_customers)
    # If no solution is found, stop the process
    if solution is None: 
        print("No solution found for the initial VRP.")
        return

    # Step 3: Extract routes from the initial solution
    routes = []
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        route = []
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route.append(node_index)
            index = solution.Value(routing.NextVar(index))
        route.append(data['depot'])  # Return to depot

        # Filter out routes that don't serve customers (depot -> depot)
        # Only include routes with customer visits
        customer_nodes_in_route = [node for node in route if node in data['customer_nodes']]
        if customer_nodes_in_route:
            routes.append(route)
    print("Routes with customers:")
    print(routes)

    # # Optionally save routes to a text file (can be omitted)
    # output_file = 'vrp_routes.txt'
    # with open(output_file, 'w') as f:
    #     f.write("Routes with customers:\n")
    #     for route in routes:
    #         f.write(" -> ".join(map(str, route)) + "\n") 

    # print("----------------------------------------------------")
    # print("\nStarting the EVRP script with dynamic charging station insertion and rerouting...")

    # Plot the initial VRP solution
    initial_vrp_output_file = f'results/initial_vrp_{num_customers}_{num_stations}_solution.png'
    plot_solution_routes(data, routes, filename=initial_vrp_output_file)

    # Adjust initial routes for EVRPTW feasibility
    initial_routes = routes  # Use the routes extracted from the initial VRP solution
    print("\nInitial Routes:")
    for route in initial_routes:
        print(route)

    updated_routes, unvisited_customers = insert_charging_stations(data, initial_routes)
    print("\nFeasible EVRPTW Routes:")
    for route in updated_routes:
        print(route)

    # Handle any unvisited customers before proceeding
    if unvisited_customers:
        print(f"Unvisited customers after initial adjustment: {unvisited_customers}")
        # Attempt to create new routes for unvisited customers
        # For simplicity, let's attempt to create single-customer routes
        for customer in unvisited_customers:
            new_route = [data['depot'], customer, data['depot']]
            updated_route = insert_charging_stations_single_route(data, new_route)
            if updated_route and is_route_feasible(data, updated_route):
                updated_routes.append(updated_route)
                print(f"Added new route for unvisited customer {customer}: {updated_route}")
            else:
                print(f"Unable to create feasible route for unvisited customer {customer}")
                # Depending on requirements, decide how to handle this case

    # Final check for unvisited customers
    all_customers = set(data['customer_nodes'])
    customers_in_routes = set(node for route in updated_routes for node in route if node in all_customers)
    remaining_unvisited_customers = all_customers - customers_in_routes

    # This if else code block stops if there is atleast one unvisited customer in feasible solution and no VNS implementation would be executed
    if remaining_unvisited_customers:
        print(f"Customers still unvisited after adjustments: {remaining_unvisited_customers}")
        print("Not all customers are visited in the initial solution. VNS may not be able to find a feasible solution.")
        # Depending on requirements, decide whether to proceed or attempt further adjustments
        return  # Exiting as VNS may not improve the solution
    else:
        # Step 5: Perform variable neighborhood search for further optimization
        print('VNS implementation starts.......\n')
        improved_routes = variable_neighborhood_search(data, updated_routes,num_customers=num_customers)
        print('VNS improved_routes:')
        for route in improved_routes:
            print(route)

        # Print and plot the final solution
        print_solution_routes(data, improved_routes)
        final_vns_output_file = f'results/EVRPTW_{num_customers}_{num_stations}_VNS_sol.png'
        plot_solution_routes(data, improved_routes, filename=final_vns_output_file)

    # # Save final VNS solution routes with customers to a text file
    # output_file = 'vns_routes.txt'
    # with open(output_file, 'w') as f:
    #     f.write("Final VNS Routes with customers:\n")
    #     for route in improved_routes:
    #         # Filter out routes that don't serve customers (i.e., depot -> depot)
    #         customer_nodes_in_route = [node for node in route if node in data['customer_nodes']]
    #         if customer_nodes_in_route:  # Only save routes with customers
    #             f.write(" -> ".join(map(str, route)) + "\n")
    # print(f"Final VNS solution saved to {output_file}")

    # Save both initial VRP routes and final VNS solution routes in a single text file
    output_file = f'results/routes_{num_customers}_{num_stations}_final_output.txt'
    with open(output_file, 'w') as f:
        # Write the header for the initial VRP routes section
        f.write("----------------------------------------------------\n")
        f.write("Initial VRP Routes with customers:\n")
        
        # Write initial VRP routes (from the `routes` variable)
        for route in routes:
            customer_nodes_in_route = [node for node in route if node in data['customer_nodes']]
            if customer_nodes_in_route:  # Only save routes with customers
                f.write(" -> ".join(map(str, route)) + "\n")

        # Separate sections for better readability
        f.write("\n----------------------------------------------------\n")
        f.write("Final VNS Routes with customers:\n")

        # Write final VNS routes (from the `improved_routes` variable)
        for route in improved_routes:
            customer_nodes_in_route = [node for node in route if node in data['customer_nodes']]
            if customer_nodes_in_route:  # Only save routes with customers
                f.write(" -> ".join(map(str, route)) + "\n")
    print(f"VRP initial and VNS final solution saved to {output_file}")
     
    # # Even if the initial solution does not cover all customers, VNS might identify better solutions that include them
    # # This if else code block executes VNS implementation even if there is customers left unvisited during feasible solution preparation

    # if remaining_unvisited_customers:
    #     print(f"Customers still unvisited after adjustments: {remaining_unvisited_customers}")
    #     print("Warning: Not all customers are visited in the initial solution. Proceeding to VNS.")
    #     # Optionally log the unvisited customers for further analysis
    #     with open('unvisited_customers_log.txt', 'w') as log_file:
    #         log_file.write("Unvisited customers after adjustments:\n")
    #         log_file.write(", ".join(map(str, remaining_unvisited_customers)) + "\n")

    # # Proceed with VNS regardless of unvisited customers
    # print('VNS implementation starts.......\n')
    # improved_routes = variable_neighborhood_search(data, updated_routes,num_customers=num_customers)

    # # After VNS, check for unvisited customers again
    # all_customers = set(data['customer_nodes'])
    # customers_in_final_routes = set(node for route in improved_routes for node in route if node in all_customers)
    # final_unvisited_customers = all_customers - customers_in_final_routes

    # if final_unvisited_customers:
    #     print(f"Warning: VNS completed but some customers are still unvisited: {final_unvisited_customers}")
    #     # Optionally log the remaining unvisited customers
    #     with open('final_unvisited_customers_log.txt', 'w') as final_log:
    #         final_log.write("Unvisited customers after VNS:\n")
    #         final_log.write(", ".join(map(str, final_unvisited_customers)) + "\n")
    # else:
    #     print("All customers are visited after VNS optimization.")

    # # Print and plot the final solution
    # print('VNS improved_routes:')
    # for route in improved_routes:
    #     print(route)
    # print_solution_routes(data, improved_routes)
    # plot_solution_routes(data, improved_routes, filename="EVRPTW_VNS_sol.png")

    # # Save final VNS solution routes with customers to a text file
    # output_file = 'vns_routes.txt'
    # with open(output_file, 'w') as f:
    #     f.write("Final VNS Routes with customers:\n")
    #     for route in improved_routes:
    #         # Filter out routes that don't serve customers (i.e., depot -> depot)
    #         customer_nodes_in_route = [node for node in route if node in data['customer_nodes']]
    #         if customer_nodes_in_route:  # Only save routes with customers
    #             f.write(" -> ".join(map(str, route)) + "\n")
    # print(f"Final VNS solution saved to {output_file}")

    # # Save both initial VRP routes and final VNS solution routes in a single text file
    # output_file = f'routes_{num_customers}_{num_stations}_final_output.txt'
    # with open(output_file, 'w') as f:
    #     # Write the header for the initial VRP routes section
    #     f.write("----------------------------------------------------\n")
    #     f.write("Initial VRP Routes with customers:\n")
        
    #     # Write initial VRP routes (from the `routes` variable)
    #     for route in routes:
    #         customer_nodes_in_route = [node for node in route if node in data['customer_nodes']]
    #         if customer_nodes_in_route:  # Only save routes with customers
    #             f.write(" -> ".join(map(str, route)) + "\n")

    #     # Separate sections for better readability
    #     f.write("\n----------------------------------------------------\n")
    #     f.write("Final VNS Routes with customers:\n")

    #     # Write final VNS routes (from the `improved_routes` variable)
    #     for route in improved_routes:
    #         customer_nodes_in_route = [node for node in route if node in data['customer_nodes']]
    #         if customer_nodes_in_route:  # Only save routes with customers
    #             f.write(" -> ".join(map(str, route)) + "\n")
    # print(f"VRP initial and VNS final solution saved to {output_file}")




if __name__ == '__main__':
    main()
