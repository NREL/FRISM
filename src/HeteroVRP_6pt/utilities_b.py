# Author: Megh KC
# ELECTRIC AND HETEROGENEOUS MIXED FLEET VARIANT OF FRISM


def flatten_route(route):
    """Flattens any nested lists in the route."""
    flat_route = []
    for item in route:
        if isinstance(item, list):
            flat_route.extend(flatten_route(item))  # Recursively flatten nested lists
        else:
            flat_route.append(item)
    return flat_route
    




def calculate_route_cost(data, route, selected_pt, charging_rate):
    """
    Calculates the cost of a single route, based on travel distances, 
    service times, and charging at inserted charging stations.
    """
    # print("selected_pt in calculate_route_cost:", selected_pt)
    # Flatten the route to ensure no nested lists
    route = flatten_route(route)
    # print(route)
    
    cost = 0
    battery_capacity = data['battery_capacities'][~1]
    # print("battery_capacity:", battery_capacity)
    battery_remaining = battery_capacity

    for i in range(len(route) - 1):
        from_node = route[i]
        to_node = route[i + 1]

        # Ensure from_node and to_node are integers for indexing into the distance matrix
        if not isinstance(from_node, int) or not isinstance(to_node, int):
            raise TypeError(f"Node identifiers must be integers, but got: from_node={from_node}, to_node={to_node}")

        # Calculate the travel distance between from_node and to_node
        distance = data['distance_matrix'][from_node][to_node]
        battery_consumption = distance
        battery_remaining -= battery_consumption
        

        # Add travel distance to cost
        cost += distance
        # print(f"From {from_node} to {to_node}: distance={distance}, battery_consumption={battery_consumption}, battery_remaining={battery_remaining}, cost={cost}")

        if to_node in data['charging_stations']:
            # print(f"the to_node {to_node} is a charging station")
            # If the next node is a charging station, calculate the charge required and update battery
            charging_amount = battery_capacity - battery_remaining
            charging_time = charging_amount * charging_rate
            # cost += charging_time
            battery_remaining = battery_capacity  # Recharge to full capacity
        elif to_node in data['customer_nodes']:
            # Access service time either from a list or dictionary
            if isinstance(data['service_times'], list):
                service_time_original = data['service_times'][to_node]
                service_time_saving = data['EV_time_savings'][to_node]
                service_time = max(0, service_time_original - service_time_saving)
            else:
                service_time =  _lookup(data.get('service_times'), to_node, (0, float('inf')))  
            cost += service_time
        # print("total_cost after service time:", cost)
        # Check if battery is depleted below zero, which should not happen with correct insertion
        if battery_remaining < 0:
            return float('inf')  # Return infinite cost for infeasible routes
    # print("final cost of the route:", cost)
    # print("selected_pt in calculate_route_cost:", selected_pt)
    # print("data['veh_pt_and_ids']:", data['veh_pt_and_ids'], "selected_pt:", selected_pt)
    pt_id = data['veh_pt_and_ids'][selected_pt]
    # print("pt_id in calculate_route_cost:", pt_id)
    total_cost_of_the_route =  cost*data['cost_per_unit_time'][pt_id] 

    return total_cost_of_the_route

def calculate_total_cost(data, routes, selected_pt, charging_rate):
    """Calculates the total cost of all routes, including charging times and vehicle fixed costs."""
    total_cost = 0
    used_vehicles = 0

    for route in routes:
        if len(route) > 2:  # Only count routes that serve at least one customer
            total_cost += calculate_route_cost(data, route,  selected_pt, charging_rate)
            # print("total_cost after each route:", total_cost)
            used_vehicles += 1
    # print("used_vehicles:", used_vehicles)
    pt_id = data['veh_pt_and_ids'][selected_pt]
    total_cost += used_vehicles * data['fixed_cost'][pt_id]  # Fixed cost per vehicle
    # print("total_cost after adding fixed cost:", total_cost)
    return total_cost


def find_best_charging_station(data, from_node, to_node):
    """Finds the best charging station to insert between two nodes."""
    min_extra_distance = float('inf')
    best_station = None
    for station in data['charging_stations']:
        distance_via_station = (data['distance_matrix'][from_node][station] +
                                data['distance_matrix'][station][to_node])
        direct_distance = data['distance_matrix'][from_node][to_node]
        extra_distance = distance_via_station - direct_distance
        if extra_distance < min_extra_distance:
            min_extra_distance = extra_distance
            best_station = station
    return best_station






def is_route_feasible(data, route):
    """Checks if a route is feasible considering battery and time window constraints."""
    if route == "infeasible":
        return False

    # Flatten route if nested lists are detected
    route = flatten_route(route)

    battery_capacity = data['battery_capacities'][~1]
    battery_remaining = battery_capacity
    arrival_time = 0  # Start at depot with departure time set to 0

    for i in range(len(route) - 1):
        from_node = route[i]
        to_node = route[i + 1]

        # Debugging statements to help trace issues
        # print(f"Checking route feasibility: from_node={from_node}, to_node={to_node}")
        
        # Check for unexpected list types in node indices
        if isinstance(from_node, list) or isinstance(to_node, list):
            print(f"Error: One of the node indices is a list after flattening. from_node={from_node}, to_node={to_node}")
            return False

        # Calculate travel distance and battery consumption
        distance = data['distance_matrix'][from_node][to_node]
        battery_consumption = distance
        travel_time = distance  # Assuming distance corresponds to travel time directly

        # Check if the vehicle has enough battery to reach the next node
        if battery_consumption > battery_remaining:
            # print(f"Battery constraint violated from {from_node} to {to_node}")
            return False  # Vehicle cannot reach the next node

        battery_remaining -= battery_consumption
        arrival_time += travel_time

        # Check if arrival time falls within the time window of the to_node
        time_window = data['time_windows'][to_node]
        if arrival_time < time_window[0]:  # Arrived early, wait until the start of the time window
            # print(f"Arrived early at node {to_node}. Waiting until time {time_window[0]}")
            arrival_time = time_window[0]
        elif arrival_time > time_window[1]:  # Arrived late, time window violated
            # print(f"Time window violated at node {to_node}. Arrival time {arrival_time}, Time window: {time_window}")
            return False

        # Set departure time based on node type
        if to_node in data['charging_stations']:
            # Recharge battery and add charging time to departure
            charging_time = (battery_capacity - battery_remaining) * data['charging_rate']
            battery_remaining = battery_capacity
            arrival_time += charging_time
            # print(f"Charging at station {to_node}. Charging time: {charging_time}, Battery recharged to full.")
        else:
            # Add service time for customer nodes
            service_time = data['service_times'][to_node]  # .get(to_node, 0)
            arrival_time += service_time
            # print(f"Serviced at node {to_node}. Service time: {service_time}")

    return True
