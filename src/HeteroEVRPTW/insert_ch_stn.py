from utilities import calculate_route_cost, calculate_total_cost, is_route_feasible, flatten_route


def flatten_route(route):
    """Flattens any nested lists in the route."""
    flat_route = []
    for item in route:
        if isinstance(item, list):
            flat_route.extend(flatten_route(item))  # Recursively flatten nested lists
        else:
            flat_route.append(item)
    return flat_route







def find_accessible_charging_station(data, current_node, battery_remaining):
    """Finds the nearest charging station that can be reached with the remaining battery."""
    min_distance = float('inf')
    nearest_station = None
    for station in data['charging_stations']:
        distance = data['distance_matrix'][current_node][station]       # Need to be adjusted if charging discharging rate is different from 1
        if distance <= battery_remaining and distance < min_distance: 
            min_distance = distance
            nearest_station = station
    return nearest_station






def insert_charging_stations_single_route(data, route, soc_threshold=0.6):
    updated_route = []
    battery_capacity = data['battery_capacities'][0]
    depot = data['depot']
    battery_remaining = battery_capacity
    arrival_time = 0
    infeasible = False

    updated_route.append(depot)
    i = 1
    while i < len(route):
        from_node = updated_route[-1]
        to_node = route[i]
        travel_time = data['distance_matrix'][from_node][to_node]
        battery_consumption = travel_time

        arrival_time += travel_time
        time_window = data['time_windows'][to_node]

        if arrival_time < time_window[0]:
            arrival_time = time_window[0]
        elif arrival_time > time_window[1]:
            infeasible = True
            break

        if battery_remaining >= battery_consumption:
            updated_route.append(to_node)
            battery_remaining -= battery_consumption

            if to_node in data['customer_nodes']:
                departure_time = arrival_time + data['service_times'][to_node]
            else:
                charging_time = (battery_capacity - battery_remaining) * data['charging_rate']
                battery_remaining = battery_capacity
                departure_time = arrival_time + charging_time

            if departure_time > time_window[1]:
                infeasible = True
                break

            arrival_time = departure_time
            i += 1
        else:
            # Attempt to find an accessible charging station
            charging_station = find_accessible_charging_station(data, from_node, battery_remaining)
            if charging_station and updated_route[-1] != charging_station:
                updated_route.append(charging_station)
                battery_remaining = battery_capacity
                charging_time = (battery_capacity - battery_remaining) * data['charging_rate']
                arrival_time += charging_time
            else:
                infeasible = True
                break

    # Attempt to return to depot if not infeasible
    if not infeasible:
        last_node = updated_route[-1]
        if last_node != depot:
            distance_to_depot = data['distance_matrix'][last_node][depot]
            if battery_remaining >= distance_to_depot:
                updated_route.append(depot)
                arrival_time += distance_to_depot
            else:
                infeasible = True

    if infeasible:
        return None  # Indicate that the route is infeasible
    else:
        return updated_route
















def insert_charging_stations(data, routes, remaining_customers, soc_threshold=0.6):
    updated_routes = []
    unvisited_customers = set()
    battery_capacity = data['battery_capacities'][0]
    depot = data['depot']

    # Use the provided remaining customers
    all_customers = set(remaining_customers)

    for route in routes:
        if not route:
            print("Warning: Empty route encountered, skipping...")
            continue

        # Use the helper function to process the route
        updated_route = insert_charging_stations_single_route(data, route)
        if updated_route is None:
            # Collect unvisited customers from the infeasible route
            unvisited_customers.update(set(node for node in route if node in remaining_customers))
        else:
            updated_routes.append(updated_route)

    # Collect unvisited customers not included in any route
    customers_in_routes = set(node for route in updated_routes for node in route if node in all_customers)
    unvisited_customers.update(all_customers - customers_in_routes)

    # Attempt to insert unvisited customers into existing routes
    for customer in unvisited_customers.copy():
        best_insertion_cost = float('inf')
        best_route_index = None
        best_position = None
        best_trial_route = None
        for route_index, route in enumerate(updated_routes):
            # Remove charging stations from route for testing insertion positions
            route_without_cs = [node for node in route if node not in data['charging_stations']]
            for pos in range(1, len(route_without_cs)):
                trial_route = route_without_cs[:pos] + [customer] + route_without_cs[pos:]
                # Use the helper function to insert charging stations
                trial_route_with_cs = insert_charging_stations_single_route(data, trial_route)
                if trial_route_with_cs is None:
                    continue  # Skip infeasible insertion
                if is_route_feasible(data, trial_route_with_cs):
                    trial_cost = calculate_route_cost(data, trial_route_with_cs, data['charging_rate'])
                    if trial_cost < best_insertion_cost:
                        best_insertion_cost = trial_cost
                        best_route_index = route_index
                        best_position = pos
                        best_trial_route = trial_route_with_cs
        if best_route_index is not None:
            # Insert customer into the best route
            updated_routes[best_route_index] = best_trial_route
            unvisited_customers.remove(customer)

    # Attempt to create new routes for any remaining unvisited customers
    while unvisited_customers:
        new_route = [depot, unvisited_customers.pop(), depot]
        # Use the helper function to insert charging stations
        updated_new_route = insert_charging_stations_single_route(data, new_route)
        if updated_new_route is not None and is_route_feasible(data, updated_new_route):
            updated_routes.append(updated_new_route)
        else:
            print(f"Unable to create a feasible route for unvisited customer.")
            # You can decide how to handle this case, e.g., report the customer as unvisited or try alternative methods

    # Final check
    customers_in_routes = set(node for route in updated_routes for node in route if node in all_customers)
    unvisited_customers = all_customers - customers_in_routes

    print(f"Final feasible updated routes: {updated_routes}")
    if unvisited_customers:
        print(f"Customers that could not be visited: {unvisited_customers}")
    return updated_routes, list(unvisited_customers)


