from utilities import calculate_total_cost, calculate_route_cost , is_route_feasible, flatten_route
import matplotlib.pyplot as plt
import numpy as np



def print_solution_routes(data, routes):
    """Prints the final feasible routes with distances, battery levels, and charging amounts to the console."""
    
    total_cost = calculate_total_cost(data, routes, data['charging_rate'])

    print('\n********************************************************')
    print(f"Total cost: {total_cost}")
    print('********************************************************\n')
    
    # Track already printed routes to avoid duplicates
    printed_routes = set()

    for vehicle_id, route in enumerate(routes):
        try:
            # Flatten route if it contains nested lists, then convert to a tuple
            route_tuple = tuple(flatten_route(route))
            if route_tuple in printed_routes:
                continue  # Skip duplicate route
            printed_routes.add(route_tuple)

            # Exclude unused vehicles (vehicles that do not serve any customers)
            customer_nodes_in_route = [node for node in route if node in data['customer_nodes']]
            if not customer_nodes_in_route:
                print(f"Warning: Vehicle {vehicle_id} did not serve any customers and only visited a charging station.")
                continue  # Skip routes that do not serve customers
            
            # Print the route details
            print(f"Route for vehicle {vehicle_id}: {route}")

            # Initialize variables for tracking
            battery_capacity = data['battery_capacities'][0]  # Assume all vehicles have the same battery capacity
            battery_remaining = battery_capacity
            total_distance = 0
            total_charging_amount = 0

            for i in range(len(route) - 1):
                from_node = route[i]
                to_node = route[i + 1]

                # Skip if the current and next nodes are the same charging station
                if from_node == to_node and to_node in data['charging_stations']:
                    continue  # Skip redundant charging station visits

                distance = data['distance_matrix'][from_node][to_node]
                total_distance += distance

                # Calculate battery consumption (1 unit distance = 1 unit battery consumption)
                battery_consumption = distance

                # Check if we're visiting a charging station
                if to_node in data['charging_stations']:
                    # Deplete battery when traveling to the charging station
                    battery_remaining -= battery_consumption

                    # Check if battery is sufficient to reach the charging station
                    if battery_remaining < 0:
                        raise RuntimeError(f"Vehicle {vehicle_id} has insufficient battery to reach charging station {to_node} from {from_node}.")

                    # Calculate the charging amount and recharge the battery
                    charging_amount = battery_capacity - battery_remaining
                    total_charging_amount += charging_amount
                    battery_remaining = battery_capacity  # Recharge to full capacity

                    print(f"  Traveling from {from_node} to {to_node} (Charging Station): Distance = {distance}, Battery Remaining = {battery_remaining}, Charging Amount = {charging_amount}")

                else:
                    # Normal travel between customer/depot nodes
                    battery_remaining -= battery_consumption

                    # Check if battery is sufficient to reach the next node
                    if battery_remaining < 0:
                        raise RuntimeError(f"Vehicle {vehicle_id} has insufficient battery to reach {to_node} from {from_node}.")

                    print(f"  Traveling from {from_node} to {to_node}: Distance = {distance}, Battery Remaining = {battery_remaining}")

            print(f"Total distance for vehicle {vehicle_id}: {total_distance}")
            print(f"Total charging amount for vehicle {vehicle_id}: {total_charging_amount}\n")

        except RuntimeError as e:
            print(f"Error in vehicle {vehicle_id}: {e}")
            # Optionally, you can log or handle the error in a more specific way

        print("----------------------------------------------------")






def plot_solution_routes(data, ice_routes, ev_routes, filename=None):
    """Plots the solution routes with separate colors for ICE and EV routes."""
    coordinates = data['locations']
    ice_color = 'red'  # Color for ICE routes
    ev_color = 'blue'  # Color for EV routes

    plt.figure(figsize=(10, 8))
    
    # Plot depot
    plt.scatter(coordinates[0][0], coordinates[0][1], color='black', s=100, label='Depot', marker='^')
    plt.text(coordinates[0][0], coordinates[0][1], 'Depot', fontsize=9)
    
    # Plot customers
    for idx in data['customer_nodes']:
        plt.scatter(coordinates[idx][0], coordinates[idx][1], color='gray', s=50, label='Customer' if idx == 1 else "", marker='o')
        plt.text(coordinates[idx][0], coordinates[idx][1], f'C{idx}', fontsize=8)
    
    # Plot charging stations
    for idx in data['charging_stations']:
        plt.scatter(coordinates[idx][0], coordinates[idx][1], color='green', s=80, label='Charging Station' if idx == data['customer_nodes'][-1] + 1 else "", marker='s')
        plt.text(coordinates[idx][0], coordinates[idx][1], f'S{idx}', fontsize=8)
    
    # Plot ICE routes
    for route_id, route in enumerate(ice_routes):
        if len(route) > 2 or (len(route) == 2 and route[0] != route[1]):
            route_coords = [coordinates[node] for node in route]
            route_coords = np.array(route_coords)
            plt.plot(route_coords[:, 0], route_coords[:, 1], color=ice_color, label=f'ICE Route {route_id}' if route_id == 0 else "")

    # Plot EV routes
    for route_id, route in enumerate(ev_routes):
        if len(route) > 2 or (len(route) == 2 and route[0] != route[1]):
            route_coords = [coordinates[node] for node in route]
            route_coords = np.array(route_coords)
            plt.plot(route_coords[:, 0], route_coords[:, 1], color=ev_color, label=f'EV Route {route_id}' if route_id == 0 else "")

    # Add labels and legend
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.legend()
    plt.grid(False)

    # Save the plot if a filename is provided
    if filename:
        plt.savefig(filename)

    # plt.show()
